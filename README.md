# Sales & Data Quality Analytics System

An end-to-end portfolio project for **Data Analyst**, **Business Analyst**, and **Data Quality Specialist** roles.

The project demonstrates how raw business data can be generated, validated, cleaned, analyzed, stored in PostgreSQL, and prepared for Power BI.

## Project Goals

This project answers five practical business questions:

1. Can the company trust the source data?
2. Which products generate the most revenue?
3. Which products have stable or unstable demand?
4. Which customers, sales channels, and managers perform best?
5. Do promotions increase revenue and sales volume?

## Tech Stack

- Python 3.12
- Pandas
- NumPy
- PostgreSQL 16
- SQLAlchemy
- Docker Compose
- pgAdmin
- Pytest
- Power BI

## Architecture

```text
Synthetic Raw Data
        |
        v
PostgreSQL: raw schema
        |
        v
Data Quality Checks
        |
        v
PostgreSQL: clean schema
        |
        v
ABC / XYZ Analysis
        |
        v
Business Analytics Marts
        |
        v
PostgreSQL: analytics schema
        |
        v
Power BI
```

## Project Structure

```text
sales_data_quality_portfolio_english/
|
|-- .env
|-- .env.example
|-- .gitignore
|-- docker-compose.yml
|-- Makefile
|-- README.md
|-- GITHUB_README_TEMPLATE.md
|
`-- app/
    |-- Dockerfile
    |-- requirements.txt
    |
    |-- src/
    |   |-- db.py
    |   |-- generate_data.py
    |   |-- load_raw.py
    |   |-- quality_report.py
    |   |-- clean_data.py
    |   |-- abc_xyz.py
    |   |-- business_analysis.py
    |   |-- create_views.py
    |   `-- run_pipeline.py
    |
    |-- sql/
    |   |-- 01_create_raw.sql
    |   `-- 02_views.sql
    |
    |-- tests/
    |   `-- test_logic.py
    |
    `-- data/
        |-- raw/
        |-- cleaned/
        `-- output/
```

## Data Model

### Products

The product master contains:

- product ID
- SKU
- barcode
- product name
- brand
- category
- cost price
- sale price

### Customers

The customer master contains:

- customer ID
- customer name
- customer type
- city
- registration date

### Sales

Each row represents one sales order line and contains:

- sales line ID
- order ID
- order date
- customer ID
- product ID
- quantity
- unit price
- discount
- revenue
- channel
- manager

### Promotions

Promotion records contain:

- promotion ID
- product ID
- start date
- end date
- discount percentage
- campaign name

## Intentional Data Quality Problems

The synthetic dataset intentionally contains errors so the project can demonstrate real data quality checks.

Examples:

- missing barcodes
- duplicate barcodes
- missing categories
- negative prices
- sale price lower than cost price
- negative sales quantity
- missing unit price
- unknown product IDs
- unknown customer IDs
- duplicate sales records

## PostgreSQL Schemas

### `raw`

Stores the original source data exactly as loaded.

Tables:

- `raw.products`
- `raw.customers`
- `raw.sales`
- `raw.promotions`

### `clean`

Stores validated and cleaned business data.

Tables:

- `clean.products`
- `clean.customers`
- `clean.sales`
- `clean.promotions`

### `analytics`

Stores analytical outputs and BI-ready marts.

Main objects:

- `analytics.data_quality_issues`
- `analytics.data_quality_summary`
- `analytics.data_quality_score`
- `analytics.product_abc_xyz`
- `analytics.fact_sales_enriched`
- `analytics.kpi_summary`
- `analytics.monthly_sales`
- `analytics.product_sales`
- `analytics.customer_sales`
- `analytics.channel_sales`
- `analytics.manager_sales`
- `analytics.promo_analysis`
- `analytics.v_sales_by_category`
- `analytics.v_sales_by_brand`
- `analytics.v_monthly_sales`

## Data Quality Dimensions

The project checks several standard data quality dimensions.

### Completeness

Checks whether required fields are missing.

Example:

```sql
SELECT *
FROM raw.products
WHERE barcode IS NULL;
```

### Uniqueness

Checks whether values that should be unique are duplicated.

Example:

```sql
SELECT
    barcode,
    COUNT(*) AS occurrences
FROM raw.products
WHERE barcode IS NOT NULL
GROUP BY barcode
HAVING COUNT(*) > 1;
```

### Validity

Checks whether values follow business rules.

Example:

```sql
SELECT *
FROM raw.products
WHERE sale_price <= 0
   OR sale_price < cost_price;
```

### Referential Integrity

Checks whether foreign-key-like references point to existing master data.

Example:

```sql
SELECT s.*
FROM raw.sales s
LEFT JOIN raw.products p
    ON s.product_id = p.product_id
WHERE p.product_id IS NULL;
```

## ABC Analysis

ABC analysis classifies products based on cumulative revenue contribution.

Default thresholds:

- A: first 80% of cumulative revenue
- B: next 15%
- C: remaining 5%

The thresholds are configurable in `.env`.

## XYZ Analysis

XYZ analysis classifies products based on demand variability.

The project uses the coefficient of variation:

```text
Coefficient of Variation = Standard Deviation / Mean
```

Default thresholds:

- X: CV <= 0.10
- Y: 0.10 < CV <= 0.25
- Z: CV > 0.25

The thresholds are configurable in `.env`.

## Promotion Analysis

For every promotion, the project compares:

- revenue before the promotion
- revenue during the promotion
- quantity before the promotion
- quantity during the promotion
- revenue uplift percentage
- quantity uplift percentage

This makes it possible to answer whether a promotion increased business performance.

## Main KPIs

The project calculates:

- total revenue
- number of orders
- number of customers
- number of products sold
- average order value
- gross profit
- gross margin percentage

## Running the Project

### 1. Start Docker

```powershell
docker compose up --build
```

The analytics pipeline runs automatically after PostgreSQL becomes healthy.

### 2. PostgreSQL connection from Windows

Use these settings in DBeaver, Power BI, or another desktop database client:

```text
Host: localhost
Port: 55432
Database: sales_quality
Username: postgres
Password: postgres
```

### 3. pgAdmin

Open:

```text
http://localhost:5050
```

Default login:

```text
Email: admin@example.com
Password: admin
```

Create a PostgreSQL server connection inside pgAdmin with:

```text
Host: db
Port: 5432
Database: sales_quality
Username: postgres
Password: postgres
```

`db` is used because pgAdmin and PostgreSQL communicate inside the Docker network.

## Re-running the Analytics Pipeline

```powershell
docker compose run --rm analytics
```

## Running Tests

```powershell
docker compose run --rm analytics pytest -q
```

Expected result:

```text
3 passed
```

## Stopping the Project

```powershell
docker compose down
```

## Full Database Reset

This command removes the PostgreSQL Docker volume:

```powershell
docker compose down -v
docker compose up --build
```

Use it only when you want to rebuild the database from scratch.

## Useful SQL Examples

### Total Revenue

```sql
SELECT
    ROUND(SUM(revenue), 2) AS total_revenue
FROM clean.sales;
```

### Number of Orders

```sql
SELECT
    COUNT(DISTINCT order_id) AS orders
FROM clean.sales;
```

### Sales by Category

```sql
SELECT *
FROM analytics.v_sales_by_category
ORDER BY revenue DESC;
```

### Top 10 Products

```sql
SELECT
    product_name,
    revenue,
    quantity,
    gross_profit
FROM analytics.product_sales
ORDER BY revenue DESC
LIMIT 10;
```

### Top Customers

```sql
SELECT
    customer_name,
    customer_type,
    city,
    revenue,
    orders,
    average_order_value
FROM analytics.customer_sales
ORDER BY revenue DESC
LIMIT 10;
```

### ABC / XYZ Distribution

```sql
SELECT
    abc_xyz_class,
    COUNT(*) AS product_count
FROM analytics.product_abc_xyz
GROUP BY abc_xyz_class
ORDER BY abc_xyz_class;
```

### Data Quality Summary

```sql
SELECT *
FROM analytics.data_quality_summary
ORDER BY error_count DESC;
```

### Promotion Performance

```sql
SELECT
    campaign_name,
    product_id,
    discount_percent,
    before_revenue,
    during_revenue,
    revenue_uplift_pct
FROM analytics.promo_analysis
ORDER BY revenue_uplift_pct DESC NULLS LAST;
```

## Recommended Power BI Pages

### 1. Executive Overview

Recommended visuals:

- Revenue card
- Orders card
- Average Order Value card
- Gross Profit card
- Gross Margin card
- Monthly revenue line chart
- Revenue by channel
- Revenue by manager

### 2. Product Analysis

Recommended visuals:

- Top products by revenue
- Revenue by category
- Revenue by brand
- ABC distribution
- XYZ distribution
- ABC/XYZ matrix

### 3. Customer Analysis

Recommended visuals:

- Top customers
- Revenue by customer type
- Revenue by city
- Customer order frequency
- Average order value

### 4. Promotion Analysis

Recommended visuals:

- Revenue before vs. during promotion
- Quantity before vs. during promotion
- Revenue uplift percentage
- Quantity uplift percentage
- Promotion performance table

### 5. Data Quality

Recommended visuals:

- Data Quality Score
- Total issue count
- Issues by type
- Issues by table
- Issues by check
- Detailed issue table

## Portfolio Value

This project demonstrates the complete analytical workflow rather than only chart creation.

It shows experience with:

- relational databases
- SQL
- data validation
- data cleaning
- Python automation
- business analysis
- product segmentation
- promotion analysis
- Docker
- BI data modeling
- automated testing

## Suggested CV Description

**Sales & Data Quality Analytics System — Portfolio Project**

Built an end-to-end analytics solution using Python, Pandas, PostgreSQL, Docker, SQL, and Power BI. Implemented automated checks for completeness, uniqueness, validity, and referential integrity; created raw, clean, and analytics data layers; performed ABC/XYZ product segmentation; analyzed customers, sales channels, managers, and promotion uplift; and produced BI-ready analytical marts for dashboarding.
