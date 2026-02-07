from psycopg import connect

from .config import settings


def check_db_connection() -> bool:
    try:
        with connect(settings.database_url, connect_timeout=2) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False
