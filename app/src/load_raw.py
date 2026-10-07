"""Create the raw PostgreSQL layer and load source CSV files."""

from pathlib import Path
import pandas as pd
from sqlalchemy import text
from db import get_engine

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
SQL_FILE = BASE_DIR / "sql" / "01_create_raw.sql"

engine = get_engine()

sql = SQL_FILE.read_text(encoding="utf-8")
with engine.begin() as conn:
    for stmt in [s.strip() for s in sql.split(";") if s.strip()]:
        conn.execute(text(stmt))

tables = {
    "products": "products.csv",
    "customers": "customers.csv",
    "sales": "sales.csv",
    "promotions": "promotions.csv",
}

date_columns = {
    "customers": ["registration_date"],
    "sales": ["order_date"],
    "promotions": ["start_date", "end_date"],
}

for table, filename in tables.items():
    df = pd.read_csv(RAW_DIR / filename)
    for col in date_columns.get(table, []):
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date

    df.to_sql(
        table,
        engine,
        schema="raw",
        if_exists="append",
        index=False,
        method="multi",
        chunksize=2000,
    )
    print(f"Loaded raw.{table}: {len(df):,}")
