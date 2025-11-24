import psycopg2
from contextlib import contextmanager
import os

POSTGRES_DB = os.getenv("POSTGRES_DB", "goats")
POSTGRES_USER = os.getenv("POSTGRES_USER", "goats")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "goats")

@contextmanager
def get_db_connection():
    #Context manager for database connections
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

with get_db_connection() as conn:
    cursor = conn.cursor()
