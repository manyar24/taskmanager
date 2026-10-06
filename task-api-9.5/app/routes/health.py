from flask import Blueprint
from sqlalchemy import text
from app.db import get_db

bp = Blueprint("health", __name__)

@bp.get("/health")
def health():
    try:
        get_db().execute(text("SELECT 1"))
        return {"data": {"status": "ok", "database": "ok"}}
    except Exception:
        return {"data": {"status": "degraded", "database": "unavailable"}}, 503
