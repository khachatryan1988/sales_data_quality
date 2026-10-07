# Sales & Data Quality Analytics System

An end-to-end analytics and Data Quality portfolio project built with **Python, Pandas, PostgreSQL, SQL, FastAPI, Docker, Excel, Chart.js, and Power BI**.

The system demonstrates a complete analytics workflow:

```text
Source Data
→ Data Ingestion
→ Data Quality Validation
→ Cleaning
→ Data Modeling
→ Business Analytics
→ Web Dashboard
→ Excel Reporting
→ Power BI
```

The project is designed as a portfolio project for roles such as:

- Data Analyst
- Data Quality Analyst
- Business Analyst
- Operations Analyst
- Sales Analyst

---

# Key Features

The application supports:

- synthetic demo data generation;
- Excel workbook upload;
- Excel structure validation;
- PostgreSQL raw data storage;
- automated Data Quality checks;
- clean data layer creation;
- ABC/XYZ product segmentation;
- business KPI calculation;
- sales analysis;
- product analysis;
- customer analysis;
- channel analysis;
- manager analysis;
- promotion effectiveness analysis;
- built-in web analytics dashboard;
- Data Quality dashboard;
- individual Data Quality issue browser;
- Excel template generation;
- sample Excel export;
- full Excel analytics report export;
- Power BI integration;
- Docker-based deployment;
- automated tests.

---

# Technology Stack

## Backend

- Python 3.12
- FastAPI
- Pandas
- NumPy
- SQLAlchemy
- psycopg2

## Database

- PostgreSQL 16
- SQL

## Data Processing

- Pandas
- openpyxl

## Visualization

- Chart.js
- Power BI

## Infrastructure

- Docker
- Docker Compose
- pgAdmin

## Testing

- pytest

---

# Architecture

```text
                    ┌─────────────────────┐
                    │    Data Sources     │
                    │                     │
                    │ Synthetic / Excel   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     raw schema      │
                    │                     │
                    │ products            │
                    │ customers           │
                    │ sales               │
                    │ promotions          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Data Quality Layer  │
                    │                     │
                    │ completeness        │
                    │ uniqueness          │
                    │ validity            │
                    │ referential checks  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    clean schema     │
                    │                     │
                    │ validated datasets  │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ analytics schema    │
                    │                     │
                    │ KPI                 │
                    │ ABC/XYZ             │
                    │ customers           │
                    │ products            │
                    │ channels            │
                    │ managers            │
                    │ promotions          │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             │                 │                 │
             ▼                 ▼                 ▼
      Web Dashboard      Excel Reports       Power BI
```

The `analytics` PostgreSQL schema is independent from the reporting tool.

This means the same analytical data can be consumed by:

- the built-in FastAPI web dashboard;
- generated Excel reports;
- Power BI;
- another external BI platform.

---

# Project Structure

```text
sales_data_quality/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Makefile
├── README.md
│
└── app/
    │
    ├── Dockerfile
    ├── requirements.txt
    │
    ├── data/
    │   ├── raw/
    │   ├── cleaned/
    │   ├── output/
    │   └── uploads/
    │
    ├── sql/
    │   ├── 01_create_raw.sql
    │   └── 02_views.sql
    │
    ├── tests/
    │   └── test_logic.py
    │
    └── src/
        │
        ├── db.py
        ├── generate_data.py
        ├── load_raw.py
        ├── quality_report.py
        ├── clean_data.py
        ├── abc_xyz.py
        ├── business_analysis.py
        ├── create_views.py
        ├── run_pipeline.py
        ├── run_uploaded_pipeline.py
        ├── excel_import.py
        │
        └── web/
            │
            ├── __init__.py
            ├── main.py
            │
            └── templates/
                ├── base.html
                ├── index.html
                ├── result.html
                ├── dashboard.html
                ├── products.html
                ├── customers.html
                ├── promotions.html
                ├── data_quality.html
                └── issues.html
```

---

# PostgreSQL Data Layers

The project uses three separate PostgreSQL schemas.

---

## 1. raw

The `raw` schema stores source data before business cleaning.

Tables:

```text
raw.products
raw.customers
raw.sales
raw.promotions
```

The raw layer preserves the original source data.

This is important because Data Quality problems must remain traceable.

---

## 2. clean

The `clean` schema contains validated data after Data Quality rules have been applied.

Tables:

```text
clean.products
clean.customers
clean.sales
clean.promotions
```

Invalid or unusable records are excluded from this layer.

---

## 3. analytics

The `analytics` schema contains business-ready analytical tables and views.

Main objects:

```text
analytics.data_quality_issues
analytics.data_quality_summary
analytics.data_quality_score

analytics.product_abc_xyz

analytics.fact_sales_enriched

analytics.kpi_summary

analytics.monthly_sales
analytics.product_sales
analytics.customer_sales
analytics.channel_sales
analytics.manager_sales
analytics.promo_analysis

analytics.v_sales_by_category
analytics.v_sales_by_brand
analytics.v_monthly_sales
```

---

# Data Quality Framework

The project validates multiple Data Quality dimensions.

---

## Completeness

Checks whether required data exists.

Examples:

```text
Missing barcode
Missing category
Missing required values
```

Example SQL:

```sql
SELECT *
FROM raw.products
WHERE barcode IS NULL;
```

---

## Uniqueness

Checks whether values that should be unique are duplicated.

Examples:

```text
Duplicate barcode
Duplicate sales records
```

Example:

```sql
SELECT
    barcode,
    COUNT(*) AS cnt
FROM raw.products
WHERE barcode IS NOT NULL
GROUP BY barcode
HAVING COUNT(*) > 1;
```

---

## Validity

Checks whether values satisfy defined business rules.

Examples:

```text
Negative quantity
Invalid price
Invalid unit price
```

---

## Referential Integrity

Checks whether referenced entities actually exist.

Example:

A sales record references a product that is missing from the product master.

```sql
SELECT s.*
FROM raw.sales s
LEFT JOIN raw.products p
    ON s.product_id = p.product_id
WHERE p.product_id IS NULL;
```

---

# Demo Dataset

The default generated dataset contains approximately:

```text
Products:        500
Customers:       500
Sales:        30,003
Promotions:       40
```

Intentional Data Quality problems are inserted into the synthetic dataset.

Examples:

- missing barcodes;
- duplicate barcodes;
- missing categories;
- invalid prices;
- negative quantity;
- invalid unit price;
- unknown product IDs;
- unknown customer IDs;
- duplicate sales records.

A typical run produces:

```text
Data Quality Issues: 105
Data Quality Score:   99.66%
Clean Products:       481
Clean Customers:      500
Clean Sales:        28,858
Clean Promotions:      39
```

The Data Quality Score is a simplified portfolio metric and is not intended to represent a universal production Data Quality methodology.

---

# Excel Upload

The application provides a browser-based Excel ingestion interface.

Open:

```text
http://localhost:8002
```

The page supports:

```text
Open Analytics Dashboard
Download Excel Template
Download Sample Excel
Upload & Run Analysis
```

---

# Required Excel Structure

An uploaded workbook must contain four sheets:

```text
products
customers
sales
promotions
```

The workbook must be:

```text
.xlsx
```

Column names must match the current PostgreSQL `raw` table structure.

---

# Excel Upload Flow

```text
Excel Workbook
      ↓
File Validation
      ↓
Sheet Validation
      ↓
Column Validation
      ↓
PostgreSQL raw
      ↓
Data Quality
      ↓
PostgreSQL clean
      ↓
ABC/XYZ
      ↓
Business Analytics
      ↓
PostgreSQL analytics
      ↓
Web Dashboard / Excel / Power BI
```

---

# Excel Template

The web application can generate an empty workbook containing the exact required database structure.

Use:

```text
Download Excel Template
```

Generated file:

```text
sales_data_template.xlsx
```

Sheets:

```text
products
customers
sales
promotions
```

---

# Sample Excel Dataset

The application can export the current PostgreSQL raw layer into Excel.

Use:

```text
Download Sample Excel
```

Generated file:

```text
sales_data_sample.xlsx
```

The sample file can be uploaded back into the system to test the complete ingestion workflow.

---

# Web Analytics Dashboard

The project includes a built-in web analytics interface.

The web dashboard uses the same PostgreSQL analytics layer as Power BI.

---

## Executive Overview

URL:

```text
http://localhost:8002/dashboard
```

Includes:

```text
Total Revenue
Orders
Average Order Value
Gross Profit
Gross Margin %

Monthly Revenue

Revenue by Channel
Revenue by Manager
Revenue by Category

Top Products
```

---

## Product Analysis

URL:

```text
http://localhost:8002/products
```

Includes:

```text
Revenue by Category
Revenue by Brand

ABC Distribution
XYZ Distribution

ABC/XYZ Matrix

Top Products
```

---

## Customer Analysis

URL:

```text
http://localhost:8002/customers
```

Includes:

```text
Revenue by City
Revenue by Customer Type
Top Customers
Orders by Customer
```

---

## Promotion Analysis

URL:

```text
http://localhost:8002/promotions
```

Includes:

```text
Revenue Before Promotion
Revenue During Promotion

Revenue Uplift %
Quantity Uplift %

Campaign Performance
```

Positive and negative uplift values are visually distinguished.

---

## Data Quality Dashboard

URL:

```text
http://localhost:8002/data-quality
```

Includes:

```text
Data Quality Score
Total Issues
Checked Rows

Issues by Type
Issues by Table
Data Quality Checks
```

---

# Data Quality Issue Details

URL:

```text
http://localhost:8002/issues
```

Displays:

```text
Check
Table
Issue Type
Row Key
Detail
```

This allows Data Quality problems to be reviewed directly from the browser without manually querying PostgreSQL.

---

# Excel Analytics Report

The system can generate a complete analytical workbook:

```text
data_quality_report.xlsx
```

The workbook contains:

```text
Summary
Issue Summary
Issues

Clean Products
Clean Customers
Clean Sales
Clean Promotions

ABC_XYZ

KPI Summary
Product Sales
Customer Sales
Channel Sales
Manager Sales
Monthly Sales

Promo Analysis
```

Exported worksheets include:

- frozen headers;
- automatic filters;
- automatically adjusted column widths.

---

# ABC Analysis

ABC analysis measures product economic importance using cumulative revenue.

Default thresholds:

```text
A = first 80% of cumulative revenue
B = next 15%
C = remaining 5%
```

Configuration:

```env
ABC_A_THRESHOLD=0.80
ABC_B_THRESHOLD=0.95
```

---

# XYZ Analysis

XYZ analysis measures demand stability.

The coefficient of variation is used:

```text
CV =
Standard Deviation / Mean
```

Default configuration:

```text
X <= 0.10
Y <= 0.25
Z > 0.25
```

Environment variables:

```env
XYZ_X_THRESHOLD=0.10
XYZ_Y_THRESHOLD=0.25
```

---

# ABC / XYZ Business Interpretation

Examples:

```text
AX
High economic importance
+
Stable demand
```

This group should usually receive high inventory availability.

```text
AZ
High economic importance
+
Unstable demand
```

This group requires more careful inventory planning.

```text
CZ
Low economic importance
+
Unstable demand
```

This group may require assortment or stock-policy review.

---

# Sales KPIs

The project calculates:

```text
Revenue
Orders
Customers
Products Sold
Average Order Value
Gross Profit
Gross Margin %
```

---

## Revenue

```text
Revenue =
Quantity × Unit Price
```

---

## Gross Profit

```text
Gross Profit =
Revenue - Gross Cost
```

---

## Gross Margin

```text
Margin % =
Gross Profit / Revenue × 100
```

---

## Average Order Value

```text
Average Order Value =
Revenue / Number of Orders
```

The project uses distinct order IDs when calculating the order count.

---

# Promotion Analysis

Promotion performance is compared with an equal-duration baseline period immediately before the campaign.

Metrics include:

```text
Revenue Before
Revenue During

Quantity Before
Quantity During

Revenue Uplift %
Quantity Uplift %
```

Formula:

```text
Revenue Uplift % =
(Revenue During - Revenue Before)
/
Revenue Before
× 100
```

In a real production environment, additional metrics should also be considered:

- gross profit;
- margin;
- seasonality;
- customer segmentation;
- control groups;
- repeat purchases.

---

# Power BI

Power BI remains fully supported.

The project deliberately keeps analytics logic outside the BI tool.

Power BI connects directly to the PostgreSQL analytics layer.

Windows connection:

```text
Host: localhost
Port: 55432
Database: sales_quality
User: postgres
Password: postgres
```

Recommended tables:

```text
analytics.kpi_summary
analytics.monthly_sales
analytics.product_sales
analytics.customer_sales
analytics.channel_sales
analytics.manager_sales
analytics.product_abc_xyz
analytics.promo_analysis
analytics.data_quality_score
analytics.data_quality_summary
analytics.data_quality_issues
```

---

# Recommended Power BI Pages

## Executive Overview

```text
Total Revenue
Orders
Average Order Value
Gross Profit
Gross Margin %

Monthly Revenue
Revenue by Channel
Revenue by Manager
```

## Product Analysis

```text
Top Products
Revenue by Category
Revenue by Brand
ABC Distribution
XYZ Distribution
ABC/XYZ Matrix
```

## Customer Analysis

```text
Top Customers
Revenue by Customer Type
Revenue by City
Average Order Value
```

## Promotion Analysis

```text
Revenue Before vs During
Revenue Uplift
Quantity Uplift
Campaign Detail
```

## Data Quality

```text
Data Quality Score
Total Issues
Issues by Type
Issues by Table
Issues by Check
Issue Detail
```

---

# Running the Project

## 1. Clone the repository

```bash
git clone https://github.com/khachatryan1988/sales_data_quality.git
```

Then:

```bash
cd sales_data_quality
```

---

# Environment Configuration

Copy:

```text
.env.example
```

to:

```text
.env
```

Example:

```env
COMPOSE_PROJECT_NAME=sales_data_quality

POSTGRES_DB=sales_quality
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

POSTGRES_HOST_PORT=55432
POSTGRES_CONTAINER_PORT=5432

DB_HOST=db

PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin
PGADMIN_HOST_PORT=5050

PRODUCT_COUNT=500
CUSTOMER_COUNT=500
SALES_COUNT=30000
PROMOTION_COUNT=40

RANDOM_SEED=42

ABC_A_THRESHOLD=0.80
ABC_B_THRESHOLD=0.95

XYZ_X_THRESHOLD=0.10
XYZ_Y_THRESHOLD=0.25
```

---

# Start Database, pgAdmin and Web Application

```bash
docker compose up -d db pgadmin web
```

Check containers:

```bash
docker compose ps
```

---

# Web Application

Open:

```text
http://localhost:8002
```

---

# Web Dashboard

Open:

```text
http://localhost:8002/dashboard
```

---

# pgAdmin

Open:

```text
http://localhost:5050
```

Example login:

```text
admin@example.com
admin
```

Inside Docker connect using:

```text
Host: db
Port: 5432
Database: sales_quality
User: postgres
Password: postgres
```

---

# DBeaver / Power BI Connection

From Windows:

```text
Host: localhost
Port: 55432
Database: sales_quality
User: postgres
Password: postgres
```

---

# Run Demo Pipeline

The original demo pipeline remains available.

Run:

```bash
docker compose run --rm analytics
```

Execution order:

```text
generate_data.py
load_raw.py
quality_report.py
clean_data.py
abc_xyz.py
business_analysis.py
create_views.py
```

Typical successful output:

```text
Raw data generated.

Loaded raw.products: 500
Loaded raw.customers: 500
Loaded raw.sales: 30,003
Loaded raw.promotions: 40

Data quality issues: 105

Clean products: 481
Clean customers: 500
Clean sales rows: 28,858
Clean promotions: 39

ABC/XYZ created.
Business analytics marts created.
Analytics views created.

PIPELINE COMPLETED SUCCESSFULLY
```

---

# Excel Upload Pipeline

Excel uploads use a separate pipeline.

Execution flow:

```text
excel_import.py
↓
raw schema
↓
quality_report.py
↓
clean_data.py
↓
abc_xyz.py
↓
business_analysis.py
↓
create_views.py
```

It intentionally does not run:

```text
generate_data.py
load_raw.py
```

because the uploaded Excel workbook is already the source dataset.

---

# Tests

Run:

```bash
docker compose run --rm analytics pytest -q
```

Current tests include:

- revenue calculation;
- margin calculation;
- duplicate detection.

---

# Example SQL Queries

## Total Revenue

```sql
SELECT
    SUM(revenue)
FROM clean.sales;
```

---

## Orders

```sql
SELECT
    COUNT(DISTINCT order_id)
FROM clean.sales;
```

---

## Top Products

```sql
SELECT *
FROM analytics.product_sales
ORDER BY revenue DESC
LIMIT 10;
```

---

## Revenue by Channel

```sql
SELECT *
FROM analytics.channel_sales
ORDER BY revenue DESC;
```

---

## Revenue by Manager

```sql
SELECT *
FROM analytics.manager_sales
ORDER BY revenue DESC;
```

---

## ABC/XYZ Distribution

```sql
SELECT
    abc_xyz_class,
    COUNT(*) AS products
FROM analytics.product_abc_xyz
GROUP BY abc_xyz_class
ORDER BY abc_xyz_class;
```

---

## Data Quality Issues

```sql
SELECT *
FROM analytics.data_quality_issues
ORDER BY
    table_name,
    check_name;
```

---

# Why the Project Uses raw / clean / analytics

The project separates responsibilities between data layers.

```text
raw
```

Preserves original source data.

```text
clean
```

Contains validated and trusted data.

```text
analytics
```

Contains business-ready tables and metrics.

This design improves:

- traceability;
- maintainability;
- Data Quality control;
- reporting performance;
- reproducibility.

---

# Why the Project Uses Both Web Dashboard and Power BI

The analytical logic does not depend on one visualization tool.

```text
PostgreSQL analytics
        ↓
    ┌───┼────────┐
    ↓   ↓        ↓
   Web Excel   Power BI
```

The built-in dashboard is useful for direct application access.

Power BI remains useful for:

- self-service BI;
- interactive reporting;
- business presentations;
- enterprise dashboards.

---

# Portfolio Skills Demonstrated

This project demonstrates practical experience with:

- Python;
- Pandas;
- SQL;
- PostgreSQL;
- Data Quality;
- data cleaning;
- relational data;
- Data Analytics;
- ABC/XYZ;
- promotion analysis;
- business KPIs;
- Excel ingestion;
- Excel reporting;
- FastAPI;
- web dashboards;
- Chart.js;
- Docker;
- Power BI;
- Git / GitHub.

---

# Interview Summary

A concise way to explain the project:

> I built an end-to-end Sales & Data Quality Analytics System using Python, Pandas, PostgreSQL, SQL, Docker, FastAPI, Excel, Chart.js, and Power BI. The system supports both synthetic data generation and Excel uploads. Data passes through raw, clean, and analytics layers. I implemented automated Data Quality checks, ABC/XYZ product segmentation, sales and promotion analytics, web dashboards, Excel reporting, and Power BI-ready analytical marts.

---

# Author

**Khachatur Khachatryan**

GitHub:

```text
https://github.com/khachatryan1988
```

Repository:

```text
https://github.com/khachatryan1988/sales_data_quality
```