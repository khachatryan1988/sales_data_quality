"""Create validated clean-layer datasets from raw PostgreSQL tables."""

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db import get_engine


BASE_DIR = Path(__file__).resolve().parents[1]

CLEAN_DIR = BASE_DIR / "data" / "cleaned"
CLEAN_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

engine = get_engine()


# ============================================================
# Drop dependent analytics views
# ============================================================
#
# The analytics views depend on tables from the clean schema.
#
# Pandas `to_sql(..., if_exists="replace")` drops the existing
# table before recreating it. PostgreSQL does not allow a table
# to be dropped while views depend on it.
#
# Therefore, the views are removed before refreshing the clean
# layer and recreated later by `create_views.py`.
# ============================================================

with engine.begin() as connection:

    connection.execute(
        text(
            """
            DROP VIEW IF EXISTS
                analytics.v_sales_by_category
            CASCADE;
            """
        )
    )

    connection.execute(
        text(
            """
            DROP VIEW IF EXISTS
                analytics.v_sales_by_brand
            CASCADE;
            """
        )
    )

    connection.execute(
        text(
            """
            DROP VIEW IF EXISTS
                analytics.v_monthly_sales
            CASCADE;
            """
        )
    )


print(
    "Dependent analytics views removed."
)


# ============================================================
# Load raw data
# ============================================================

products = pd.read_sql(
    "SELECT * FROM raw.products",
    engine,
)

customers = pd.read_sql(
    "SELECT * FROM raw.customers",
    engine,
)

sales = pd.read_sql(
    "SELECT * FROM raw.sales",
    engine,
)

promotions = pd.read_sql(
    "SELECT * FROM raw.promotions",
    engine,
)


# ============================================================
# Clean products
# ============================================================

products = products.dropna(
    subset=[
        "product_id",
        "sku",
        "product_name",
        "barcode",
        "category",
    ]
)


# Remove duplicate product IDs.
products = products.drop_duplicates(
    subset=["product_id"],
    keep="first",
)


# Remove duplicate SKUs.
products = products.drop_duplicates(
    subset=["sku"],
    keep="first",
)


# Remove duplicate barcodes.
products = products.drop_duplicates(
    subset=["barcode"],
    keep="first",
)


# Apply product price business rules.
products = products[
    (products["cost_price"] > 0)
    & (products["sale_price"] > 0)
    & (
            products["sale_price"]
            >= products["cost_price"]
    )
    ].copy()


# ============================================================
# Clean customers
# ============================================================

customers = customers.dropna(
    subset=[
        "customer_id",
        "customer_name",
    ]
)


customers = customers.drop_duplicates(
    subset=["customer_id"],
    keep="first",
)


# ============================================================
# Prepare valid master-data IDs
# ============================================================

valid_product_ids = set(
    products["product_id"]
)

valid_customer_ids = set(
    customers["customer_id"]
)


# ============================================================
# Clean sales
# ============================================================

# Keep only sales referencing valid products and customers.
sales = sales[
    sales["product_id"].isin(
        valid_product_ids
    )
    &
    sales["customer_id"].isin(
        valid_customer_ids
    )
    ].copy()


# Apply sales business rules.
sales = sales[
    (sales["quantity"] > 0)
    & sales["unit_price"].notna()
    & (sales["unit_price"] > 0)
    & sales["revenue"].notna()
    & (sales["revenue"] >= 0)
    ].copy()


# These columns define whether two sales rows represent
# the same business transaction line.
business_columns = [
    "order_id",
    "order_date",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "discount",
    "revenue",
    "channel",
    "manager",
]


sales = sales.drop_duplicates(
    subset=business_columns,
    keep="first",
)


# ============================================================
# Clean promotions
# ============================================================

promotions["start_date"] = (
    pd.to_datetime(
        promotions["start_date"]
    )
)

promotions["end_date"] = (
    pd.to_datetime(
        promotions["end_date"]
    )
)


promotions = promotions[
    promotions["product_id"].isin(
        valid_product_ids
    )
    &
    (
            promotions["end_date"]
            >= promotions["start_date"]
    )
    &
    promotions[
        "discount_percent"
    ].between(
        0,
        100,
    )
    ].copy()


# ============================================================
# Export clean CSV files
# ============================================================

products.to_csv(
    CLEAN_DIR / "products_clean.csv",
    index=False,
    encoding="utf-8-sig",
    )

customers.to_csv(
    CLEAN_DIR / "customers_clean.csv",
    index=False,
    encoding="utf-8-sig",
    )

sales.to_csv(
    CLEAN_DIR / "sales_clean.csv",
    index=False,
    encoding="utf-8-sig",
    )

promotions.to_csv(
    CLEAN_DIR / "promotions_clean.csv",
    index=False,
    encoding="utf-8-sig",
    )


# ============================================================
# Rebuild the PostgreSQL clean layer
# ============================================================

products.to_sql(
    "products",
    engine,
    schema="clean",
    if_exists="replace",
    index=False,
)


customers.to_sql(
    "customers",
    engine,
    schema="clean",
    if_exists="replace",
    index=False,
)


sales.to_sql(
    "sales",
    engine,
    schema="clean",
    if_exists="replace",
    index=False,
)


promotions.to_sql(
    "promotions",
    engine,
    schema="clean",
    if_exists="replace",
    index=False,
)


# ============================================================
# Summary
# ============================================================

print(
    "Clean layer created successfully."
)

print(
    f"Clean products: {len(products):,}"
)

print(
    f"Clean customers: {len(customers):,}"
)

print(
    f"Clean sales rows: {len(sales):,}"
)

print(
    f"Clean promotions: {len(promotions):,}"
)