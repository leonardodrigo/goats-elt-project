import psycopg2
import psycopg2.extras
import psycopg2.sql as sql
import logging
from typing import List, Sequence, Optional, Any, Iterable, Dict
import json

from src.api.clients.minio import MinIOClient

logging.getLogger(__name__).addHandler(logging.NullHandler())


class PostgresClient:
    def __init__(
        self, host: str, port: int, database: str, user: str, password: str
    ) -> None:
        """
        Simple PG client wrapper.

        Args:
          host, port, database, user, password: connection params
        """
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn: Optional[psycopg2.extensions.connection] = None

    def connect(self) -> None:
        """Open a new connection (no-op if already open)."""
        if self.conn and not self.conn.closed:
            return
        conn_args = dict(
            host=self.host,
            port=self.port,
            dbname=self.database,
            user=self.user,
            password=self.password,
        )
        self.conn = psycopg2.connect(**conn_args)
        # return rows as dict-like objects for convenience
        self.conn.autocommit = True

    def close(self) -> None:
        """Close connection if open."""
        if self.conn and not self.conn.closed:
            try:
                self.conn.close()
            finally:
                self.conn = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _read_bytes_to_objects(
        self, data_bytes: bytes, file_format: str = "jsonl", encoding: str = "utf-8"
    ):
        text = data_bytes.decode(encoding)
        if file_format == "jsonl":
            return (json.loads(line) for line in text.splitlines() if line.strip())
        else:
            data = json.loads(text)
            if not isinstance(data, list):
                raise ValueError("json_array format requires top-level list")
            return data

    def _create_table_for_json(
        self,
        schema: str,
        table: str,
        other_columns: Sequence[str] = None,
        data_column: str = "data",
    ) -> None:
        """
        Create a table suitable for storing JSON objects.
        Other columns default to TEXT. Data column is JSONB.
        Uses CREATE TABLE IF NOT EXISTS to be idempotent.
        """
        self.connect()
        # build column definitions
        cols_defs = []
        if other_columns:
            for c in other_columns:
                cols_defs.append(sql.SQL("{} TEXT").format(sql.Identifier(c)))
        cols_defs.append(sql.SQL("{} JSONB").format(sql.Identifier(data_column)))
        create_sql = sql.SQL("CREATE TABLE IF NOT EXISTS {table} ({cols})").format(
            table=sql.Identifier(schema, table), cols=sql.SQL(", ").join(cols_defs)
        )
        logging.info(f"Create table SQL: {create_sql.as_string(self.conn)}")
        try:
            with self.conn.cursor() as cur:
                cur.execute(create_sql.as_string(self.conn))
        except psycopg2.errors.InvalidSchemaName as e:
            logging.warning(f"Schema {schema} does not exist. Creating schema...")
            with self.conn.cursor() as cur:
                cur.execute(
                    sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                        sql.Identifier(schema)
                    )
                )
                cur.execute(create_sql.as_string(self.conn))

    def insert_json_objects(
        self,
        schema: str,
        table: str,
        rows: Iterable[dict],
        data_column: str = "data",
        other_columns: Optional[Sequence[str]] = None,
    ) -> None:
        """
        Bulk insert python dicts into a table where one column stores the JSON/JSONB object.
        - rows: iterable of dicts (each dict becomes the JSON value stored in data_column)
        - other_columns: optional list of column names to extract from each dict (order matters)
        Example:
            pg.insert_json_objects("events", rows, data_column="payload", other_columns=["id","ts"])
        """
        rows = list(rows)
        if not rows:
            return
        self.connect()
        other_columns = list(other_columns) if other_columns else []
        cols = other_columns + [data_column]
        cols_sql = sql.SQL(", ").join(map(sql.Identifier, cols))
        insert_sql = sql.SQL("INSERT INTO {table} ({cols}) VALUES %s").format(
            table=sql.Identifier(schema, table), cols=cols_sql
        )
        values = []
        for obj in rows:
            row_vals = []
            for c in other_columns:
                row_vals.append(obj.get(c))
            row_vals.append(psycopg2.extras.Json(obj))
            values.append(tuple(row_vals))

        try:
            with self.conn.cursor() as cur:
                psycopg2.extras.execute_values(
                    cur,
                    insert_sql.as_string(self.conn),
                    values,
                    template=None,
                    page_size=1000,
                )
        except psycopg2.errors.UndefinedTable:
            logging.warning(f"Table {schema}.{table} does not exist. Creating table...")
            self._create_table_for_json(schema, table, other_columns, data_column)
            with self.conn.cursor() as cur:
                psycopg2.extras.execute_values(
                    cur,
                    insert_sql.as_string(self.conn),
                    values,
                    template=None,
                    page_size=1000,
                )

    def insert_json_file(
        self,
        filepath: str,
        schema: str,
        table: str,
        data_column: str = "data",
        other_columns: Optional[Sequence[str]] = None,
        file_format: str = "jsonl",
        encoding: str = "utf-8",
    ) -> None:
        """
        Read a local JSON file and insert.
        - file_format: "jsonl" (newline delimited) or "json_array" (top-level array)
        """
        with open(filepath, "r", encoding=encoding) as f:
            if file_format == "jsonl":
                objs = (json.loads(line) for line in f if line.strip())
                self.insert_json_objects(
                    schema,
                    table,
                    objs,
                    data_column=data_column,
                    other_columns=other_columns,
                )
            else:
                data = json.load(f)
                if not isinstance(data, list):
                    raise ValueError("json_array format requires top-level list")
                self.insert_json_objects(
                    schema,
                    table,
                    data,
                    data_column=data_column,
                    other_columns=other_columns,
                )

    def insert_json_from_minio(
        self,
        minio_client: MinIOClient,
        object_name: str,
        schema: str,
        table: str,
        data_column: str = "data",
        other_columns: Optional[Sequence[str]] = None,
        file_format: str = "jsonl",
    ) -> None:
        """
        Download a file from MinIO (S3-compatible) and insert JSON objects.
        Requires minio package if used.
        """
        try:
            resp = minio_client.read_object(object_name)

        except Exception as e:
            logging.error(f"Error reading data from MinIO object {object_name}: {e}")
            return
        # objs = self._read_bytes_to_objects(data_bytes, file_format=file_format)
        logging.info(f"minio object:{resp}")
        self.insert_json_objects(
            schema, table, resp, data_column=data_column, other_columns=other_columns
        )

    def execute_query(
        self, query: str, params: Optional[Sequence[Any]] = None, fetch: bool = False
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Execute an arbitrary query.
        If fetch is True returns list of rows as dicts, otherwise returns None.
        """
        self.connect()
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
        return None

    def fetch_all(
        self,
        table: str,
        columns: Iterable[str] = ("*",),
        where: Optional[str] = None,
        params: Optional[Sequence[Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """SELECT rows from table and return list of dicts."""
        cols_sql = sql.SQL(", ").join(
            [sql.Identifier(c) if c != "*" else sql.SQL("*") for c in columns]
        )
        q = sql.SQL("SELECT {cols} FROM {table}").format(
            cols=cols_sql, table=sql.Identifier(table)
        )
        if where:
            q = sql.SQL("{} WHERE {}").format(q, sql.SQL(where))
        if limit:
            q = sql.SQL("{} LIMIT {}").format(q, sql.Literal(limit))
        return (
            self.execute_query(q.as_string(self.conn), params=params, fetch=True) or []
        )
