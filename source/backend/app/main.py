from fastapi import FastAPI

from .config import settings
from .db import check_db_connection

app = FastAPI(title=settings.app_name)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.get("/health/db")
def health_db() -> dict:
    ok = check_db_connection()
    return {"status": "ok" if ok else "error", "database": ok}
