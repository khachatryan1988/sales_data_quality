"""Basic unit tests for business formulas and data-quality logic."""

import pandas as pd

def test_revenue_formula():
    quantity = 3
    price = 5000
    discount = 0.10
    revenue = quantity * price * (1 - discount)
    assert revenue == 13500

def test_margin_formula():
    revenue = 10000
    gross_profit = 2500
    margin = gross_profit / revenue * 100
    assert margin == 25.0

def test_duplicate_detection():
    df = pd.DataFrame({"barcode": ["1", "2", "2", "3"]})
    duplicates = df["barcode"].duplicated(keep=False).sum()
    assert duplicates == 2
