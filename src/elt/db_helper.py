import psycopg2
from contextlib import contextmanager
import os

DATABASE_URL = os.getenv("DATABASE_URL", "goats_elt")
POSTGRES_USER = os.getenv("POSTGRES_USER","myuser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD","mypassword")

@contextmanager
def get_db_connection():
    #Context manager for database connections
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname=DATABASE_URL,
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
