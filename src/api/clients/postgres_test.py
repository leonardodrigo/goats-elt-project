import psycopg2
from contextlib import contextmanager

POSTGRES_DB = "dbt"
POSTGRES_USER = "goats"
POSTGRES_PASSWORD = "goats"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5433


@contextmanager
def get_db_connection():
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("Error:", e)
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    print("Testing connection...")

    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        print("Success:", cur.fetchone())
