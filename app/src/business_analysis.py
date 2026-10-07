"""Build BI-ready business analytics marts and promotion analysis outputs."""

from pathlib import Path
import pandas as pd
from db import get_engine

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

engine = get_engine()

sales = pd.read_sql("SELECT * FROM clean.sales", engine)
products = pd.read_sql("SELECT * FROM clean.products", engine)
customers = pd.read_sql("SELECT * FROM clean.customers", engine)
promotions = pd.read_sql("SELECT * FROM clean.promotions", engine)

sales["order_date"] = pd.to_datetime(sales["order_date"])
promotions["start_date"] = pd.to_datetime(promotions["start_date"])
promotions["end_date"] = pd.to_datetime(promotions["end_date"])

fact = (
    sales.merge(
        products[["product_id", "sku", "product_name", "brand", "category", "cost_price"]],
        on="product_id",
        how="left",
    )
    .merge(
        customers[["customer_id", "customer_name", "customer_type", "city"]],
        on="customer_id",
        how="left",
    )
)

fact["gross_cost"] = fact["quantity"] * fact["cost_price"]
fact["gross_profit"] = fact["revenue"] - fact["gross_cost"]
fact["margin_pct"] = fact["gross_profit"] / fact["revenue"].replace(0, pd.NA) * 100
fact["year"] = fact["order_date"].dt.year
fact["month"] = fact["order_date"].dt.month
fact["year_month"] = fact["order_date"].dt.to_period("M").astype(str)

orders = fact["order_id"].nunique()
revenue = fact["revenue"].sum()
gross_profit = fact["gross_profit"].sum()

kpi = pd.DataFrame([{
    "revenue": round(revenue, 2),
    "orders": int(orders),
    "customers": int(fact["customer_id"].nunique()),
    "products_sold": int(fact["product_id"].nunique()),
    "average_check": round(revenue / orders, 2) if orders else 0,
    "gross_profit": round(gross_profit, 2),
    "margin_pct": round(gross_profit / revenue * 100, 2) if revenue else 0,
}])

monthly_sales = (
    fact.groupby("year_month", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
        gross_profit=("gross_profit", "sum"),
        quantity=("quantity", "sum"),
    )
)

product_sales = (
    fact.groupby(["product_id", "sku", "product_name", "brand", "category"], as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        quantity=("quantity", "sum"),
        gross_profit=("gross_profit", "sum"),
        orders=("order_id", "nunique"),
    )
    .sort_values("revenue", ascending=False)
)

customer_sales = (
    fact.groupby(["customer_id", "customer_name", "customer_type", "city"], as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
        gross_profit=("gross_profit", "sum"),
    )
)
customer_sales["average_order_value"] = customer_sales["revenue"] / customer_sales["orders"]

channel_sales = (
    fact.groupby("channel", as_index=False)
    .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
)

manager_sales = (
    fact.groupby("manager", as_index=False)
    .agg(revenue=("revenue", "sum"), orders=("order_id", "nunique"))
)

promo_rows = []
for _, promo in promotions.iterrows():
    product_sales_rows = fact[fact["product_id"] == promo["product_id"]].copy()
    if product_sales_rows.empty:
        continue

    start = promo["start_date"]
    end = promo["end_date"]
    duration = (end - start).days + 1
    before_start = start - pd.Timedelta(days=duration)
    before_end = start - pd.Timedelta(days=1)

    during = product_sales_rows[
        (product_sales_rows["order_date"] >= start)
        & (product_sales_rows["order_date"] <= end)
    ]
    before = product_sales_rows[
        (product_sales_rows["order_date"] >= before_start)
        & (product_sales_rows["order_date"] <= before_end)
    ]

    before_revenue = before["revenue"].sum()
    during_revenue = during["revenue"].sum()
    before_qty = before["quantity"].sum()
    during_qty = during["quantity"].sum()

    revenue_uplift_pct = (
        ((during_revenue - before_revenue) / before_revenue * 100)
        if before_revenue else None
    )
    quantity_uplift_pct = (
        ((during_qty - before_qty) / before_qty * 100)
        if before_qty else None
    )

    promo_rows.append({
        "promotion_id": promo["promotion_id"],
        "campaign_name": promo["campaign_name"],
        "product_id": promo["product_id"],
        "discount_percent": promo["discount_percent"],
        "before_revenue": round(before_revenue, 2),
        "during_revenue": round(during_revenue, 2),
        "revenue_uplift_pct": round(revenue_uplift_pct, 2) if revenue_uplift_pct is not None else None,
        "before_quantity": float(before_qty),
        "during_quantity": float(during_qty),
        "quantity_uplift_pct": round(quantity_uplift_pct, 2) if quantity_uplift_pct is not None else None,
    })

promo_analysis = pd.DataFrame(promo_rows)

outputs = {
    "fact_sales_enriched": fact,
    "kpi_summary": kpi,
    "monthly_sales": monthly_sales,
    "product_sales": product_sales,
    "customer_sales": customer_sales,
    "channel_sales": channel_sales,
    "manager_sales": manager_sales,
    "promo_analysis": promo_analysis,
}

for name, df in outputs.items():
    df.to_csv(OUTPUT_DIR / f"{name}.csv", index=False, encoding="utf-8-sig")
    df.to_sql(name, engine, schema="analytics", if_exists="replace", index=False)

print("Business analytics marts created.")
