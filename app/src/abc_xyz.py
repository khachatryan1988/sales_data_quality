"""Perform ABC revenue segmentation and XYZ demand-variability analysis."""

from pathlib import Path
import os
import numpy as np
import pandas as pd
from db import get_engine

BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_DIR = BASE_DIR / "data" / "cleaned"
OUTPUT_DIR = BASE_DIR / "data" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ABC_A = float(os.getenv("ABC_A_THRESHOLD", "0.80"))
ABC_B = float(os.getenv("ABC_B_THRESHOLD", "0.95"))
XYZ_X = float(os.getenv("XYZ_X_THRESHOLD", "0.10"))
XYZ_Y = float(os.getenv("XYZ_Y_THRESHOLD", "0.25"))

sales = pd.read_csv(CLEAN_DIR / "sales_clean.csv")
products = pd.read_csv(CLEAN_DIR / "products_clean.csv")
sales["order_date"] = pd.to_datetime(sales["order_date"])
sales["month"] = sales["order_date"].dt.to_period("M").astype(str)

abc = (
    sales.groupby("product_id", as_index=False)["revenue"]
    .sum()
    .rename(columns={"revenue": "total_revenue"})
    .sort_values("total_revenue", ascending=False)
)
abc["revenue_share"] = abc["total_revenue"] / abc["total_revenue"].sum()
abc["cumulative_share"] = abc["revenue_share"].cumsum()
abc["abc_class"] = abc["cumulative_share"].apply(
    lambda x: "A" if x <= ABC_A else ("B" if x <= ABC_B else "C")
)

monthly = sales.groupby(["product_id", "month"], as_index=False)["quantity"].sum()
pivot = monthly.pivot(index="product_id", columns="month", values="quantity").fillna(0)

mean_qty = pivot.mean(axis=1)
std_qty = pivot.std(axis=1, ddof=0)
cv = np.where(mean_qty > 0, std_qty / mean_qty, np.nan)

xyz = pd.DataFrame({
    "product_id": pivot.index,
    "avg_monthly_qty": mean_qty.values,
    "std_monthly_qty": std_qty.values,
    "coefficient_of_variation": cv,
})
xyz["xyz_class"] = xyz["coefficient_of_variation"].apply(
    lambda x: "Z" if pd.isna(x) else ("X" if x <= XYZ_X else ("Y" if x <= XYZ_Y else "Z"))
)

result = (
    products[["product_id", "sku", "product_name", "brand", "category"]]
    .merge(abc, on="product_id", how="left")
    .merge(xyz, on="product_id", how="left")
)
result["abc_class"] = result["abc_class"].fillna("C")
result["xyz_class"] = result["xyz_class"].fillna("Z")
result["abc_xyz_class"] = result["abc_class"] + result["xyz_class"]

result.to_csv(OUTPUT_DIR / "product_abc_xyz.csv", index=False, encoding="utf-8-sig")
result.to_sql("product_abc_xyz", get_engine(), schema="analytics", if_exists="replace", index=False)

print("ABC/XYZ created.")
