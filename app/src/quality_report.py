"""Run automated data-quality checks and store issue-level results."""

from pathlib import Path
import pandas as pd
from db import get_engine

BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "data" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

engine = get_engine()

products = pd.read_sql("SELECT * FROM raw.products", engine)
customers = pd.read_sql("SELECT * FROM raw.customers", engine)
sales = pd.read_sql("SELECT * FROM raw.sales", engine)

product_ids = set(products["product_id"].dropna())
customer_ids = set(customers["customer_id"].dropna())
business_cols = [
    "order_id", "order_date", "customer_id", "product_id",
    "quantity", "unit_price", "discount", "revenue", "channel", "manager"
]

issues = []

def add_issue(check_name, table_name, issue_type, row_key, detail):
    issues.append({
        "check_name": check_name,
        "table_name": table_name,
        "issue_type": issue_type,
        "row_key": str(row_key),
        "detail": detail,
    })

for _, r in products[products["barcode"].isna()].iterrows():
    add_issue("Missing barcode", "products", "completeness", r["product_id"], "barcode is NULL")

dup_barcodes = products["barcode"].dropna()
dup_values = dup_barcodes[dup_barcodes.duplicated(keep=False)].unique()
for barcode in dup_values:
    rows = products[products["barcode"] == barcode]
    for _, r in rows.iterrows():
        add_issue("Duplicate barcode", "products", "uniqueness", r["product_id"], f"barcode={barcode}")

for _, r in products[products["category"].isna()].iterrows():
    add_issue("Missing category", "products", "completeness", r["product_id"], "category is NULL")

bad_price_mask = (
    (products["cost_price"] <= 0)
    | (products["sale_price"] <= 0)
    | (products["sale_price"] < products["cost_price"])
)
for _, r in products[bad_price_mask].iterrows():
    add_issue("Invalid product prices", "products", "validity", r["product_id"],
              f"cost={r['cost_price']}, sale={r['sale_price']}")

for _, r in sales[sales["quantity"] <= 0].iterrows():
    add_issue("Invalid quantity", "sales", "validity", r["sales_line_id"], f"quantity={r['quantity']}")

bad_unit = sales["unit_price"].isna() | (sales["unit_price"] <= 0)
for _, r in sales[bad_unit].iterrows():
    add_issue("Missing or invalid unit_price", "sales", "validity", r["sales_line_id"],
              f"unit_price={r['unit_price']}")

for _, r in sales[~sales["product_id"].isin(product_ids)].iterrows():
    add_issue("Unknown product_id", "sales", "referential_integrity", r["sales_line_id"],
              f"product_id={r['product_id']}")

for _, r in sales[~sales["customer_id"].isin(customer_ids)].iterrows():
    add_issue("Unknown customer_id", "sales", "referential_integrity", r["sales_line_id"],
              f"customer_id={r['customer_id']}")

dups = sales[sales.duplicated(subset=business_cols, keep=False)]
for _, r in dups.iterrows():
    add_issue("Duplicate sales row", "sales", "uniqueness", r["sales_line_id"], f"order_id={r['order_id']}")

issues_df = pd.DataFrame(issues)

summary = (
    issues_df.groupby(["check_name", "table_name", "issue_type"], as_index=False)
    .size()
    .rename(columns={"size": "error_count"})
)

total_raw_rows = len(products) + len(customers) + len(sales)
score = 100 - ((len(issues_df) / total_raw_rows) * 100)

score_df = pd.DataFrame([{
    "data_quality_score_pct": round(score, 2),
    "total_detected_issues": len(issues_df),
    "checked_rows": total_raw_rows,
}])

issues_df.to_csv(OUTPUT_DIR / "data_quality_issues.csv", index=False, encoding="utf-8-sig")
summary.to_csv(OUTPUT_DIR / "data_quality_summary.csv", index=False, encoding="utf-8-sig")
score_df.to_csv(OUTPUT_DIR / "data_quality_score.csv", index=False, encoding="utf-8-sig")

issues_df.to_sql("data_quality_issues", engine, schema="analytics", if_exists="replace", index=False)
summary.to_sql("data_quality_summary", engine, schema="analytics", if_exists="replace", index=False)
score_df.to_sql("data_quality_score", engine, schema="analytics", if_exists="replace", index=False)

print(f"Data quality issues: {len(issues_df)}")
print(score_df.to_string(index=False))
