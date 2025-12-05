import psycopg2
from contextlib import contextmanager
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

POSTGRES_DB = os.getenv("POSTGRES_DB", "dbt")
POSTGRES_USER = os.getenv("POSTGRES_USER", "goats")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "goats")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")


@contextmanager
def get_db_connection():
    # Context manager for database connections
    conn = psycopg2.connect(
        host=POSTGRES_HOST,
        port=5432,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    )
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()
