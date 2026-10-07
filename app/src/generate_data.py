"""Generate synthetic business data and intentional data-quality issues."""

from pathlib import Path
from datetime import datetime, timedelta
import os
import random
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))
PRODUCT_COUNT = int(os.getenv("PRODUCT_COUNT", "500"))
CUSTOMER_COUNT = int(os.getenv("CUSTOMER_COUNT", "500"))
SALES_COUNT = int(os.getenv("SALES_COUNT", "30000"))
PROMOTION_COUNT = int(os.getenv("PROMOTION_COUNT", "40"))

random.seed(RANDOM_SEED)

brands = ["Aroma", "Barista Pro", "Dolce", "Premium Food", "Fresh Line", "Royal Taste"]
categories = ["Coffee", "Tea", "Chocolate", "Syrup", "Cream", "Bakery"]
channels = ["Retail", "Online", "B2B"]
managers = ["Manager A", "Manager B", "Manager C", "Manager D"]

products = []
for i in range(1, PRODUCT_COUNT + 1):
    cost = random.randint(500, 15000)
    markup = random.uniform(1.15, 1.80)
    products.append({
        "product_id": i,
        "sku": f"SKU-{i:05d}",
        "barcode": f"485000{i:07d}",
        "product_name": f"Product {i}",
        "brand": random.choice(brands),
        "category": random.choice(categories),
        "cost_price": float(cost),
        "sale_price": round(cost * markup, 2),
    })

products_df = pd.DataFrame(products)

for idx in random.sample(range(len(products_df)), min(10, len(products_df))):
    products_df.loc[idx, "barcode"] = None

if len(products_df) > 51:
    products_df.loc[20, "barcode"] = products_df.loc[19, "barcode"]
    products_df.loc[50, "barcode"] = products_df.loc[49, "barcode"]

for idx in random.sample(range(len(products_df)), min(5, len(products_df))):
    products_df.loc[idx, "category"] = None

if len(products_df) > 120:
    products_df.loc[100, "sale_price"] = -5000
    products_df.loc[120, "sale_price"] = products_df.loc[120, "cost_price"] - 100

products_df.to_csv(RAW_DIR / "products.csv", index=False, encoding="utf-8-sig")

customer_types = ["HoReCa", "Retail", "Distributor", "Hotel", "Cafe"]
cities = ["Yerevan", "Gyumri", "Vanadzor", "Abovyan", "Hrazdan"]

customers = []
for i in range(1, CUSTOMER_COUNT + 1):
    customers.append({
        "customer_id": i,
        "customer_name": f"Customer {i}",
        "customer_type": random.choice(customer_types),
        "city": random.choice(cities),
        "registration_date": (
            datetime(2024, 1, 1) + timedelta(days=random.randint(0, 730))
        ).date()
    })

customers_df = pd.DataFrame(customers)
customers_df.to_csv(RAW_DIR / "customers.csv", index=False, encoding="utf-8-sig")

sales = []
start_date = datetime(2025, 1, 1)
sales_line_id = 1
order_id = 100000

for _ in range(SALES_COUNT):
    product_id = random.randint(1, PRODUCT_COUNT)
    customer_id = random.randint(1, CUSTOMER_COUNT)
    product = products_df.loc[products_df["product_id"] == product_id].iloc[0]

    quantity = random.randint(1, 10)
    unit_price = float(product["sale_price"])
    discount = random.choice([0, 0, 0, 0.05, 0.10, 0.15])
    order_date = start_date + timedelta(days=random.randint(0, 637))
    revenue = quantity * unit_price * (1 - discount)

    sales.append({
        "sales_line_id": sales_line_id,
        "order_id": order_id,
        "order_date": order_date.date(),
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
        "unit_price": unit_price,
        "discount": discount,
        "revenue": round(revenue, 2),
        "channel": random.choice(channels),
        "manager": random.choice(managers),
    })

    sales_line_id += 1
    if random.random() >= 0.35:
        order_id += 1

sales_df = pd.DataFrame(sales)

if len(sales_df) > 900:
    sales_df.loc[200, "customer_id"] = CUSTOMER_COUNT + 9999
    sales_df.loc[500, "product_id"] = PRODUCT_COUNT + 9999
    sales_df.loc[700, "quantity"] = -3
    sales_df.loc[900, "unit_price"] = None

if len(sales_df) > 1002:
    dup = sales_df.iloc[[1000, 1001, 1002]].copy()
    max_id = int(sales_df["sales_line_id"].max())
    dup["sales_line_id"] = range(max_id + 1, max_id + 4)
    sales_df = pd.concat([sales_df, dup], ignore_index=True)

sales_df.to_csv(RAW_DIR / "sales.csv", index=False, encoding="utf-8-sig")

promotions = []
for i in range(1, PROMOTION_COUNT + 1):
    product_id = random.randint(1, PRODUCT_COUNT)
    start = datetime(2025, 2, 1) + timedelta(days=random.randint(0, 500))
    duration = random.randint(7, 30)
    promotions.append({
        "promotion_id": i,
        "product_id": product_id,
        "start_date": start.date(),
        "end_date": (start + timedelta(days=duration)).date(),
        "discount_percent": random.choice([5, 10, 15, 20]),
        "campaign_name": f"Promo {i}",
    })

promotions_df = pd.DataFrame(promotions)
promotions_df.to_csv(RAW_DIR / "promotions.csv", index=False, encoding="utf-8-sig")

print("Raw data generated.")
