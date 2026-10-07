"""Create reusable PostgreSQL analytics views."""

from pathlib import Path
from sqlalchemy import text
from db import get_engine

BASE_DIR = Path(__file__).resolve().parents[1]
sql = (BASE_DIR / "sql" / "02_views.sql").read_text(encoding="utf-8")
engine = get_engine()

with engine.begin() as conn:
    for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
        conn.execute(text(stmt))

print("Analytics views created.")
