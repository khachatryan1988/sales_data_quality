# Sales & Data Quality Analytics System

An end-to-end portfolio project for **Data Analyst**, **Business Analyst**, and **Data Quality Analyst** roles.

The project demonstrates how raw business data can be generated or uploaded from Excel, validated, cleaned, analyzed, stored in PostgreSQL, exported to Excel, and prepared for Power BI reporting.

---

## Project Overview

The system supports two data ingestion workflows:

### Demo Data Mode

```text
Synthetic Data Generation
        ↓
PostgreSQL Raw Layer
        ↓
Data Quality Validation
        ↓
Clean Layer
        ↓
Business Analytics
        ↓
Power BI
```

### Excel Upload Mode

```text
Excel Workbook
        ↓
Structure Validation
        ↓
PostgreSQL Raw Layer
        ↓
Data Quality Validation
        ↓
Clean Layer
        ↓
ABC/XYZ Analysis
        ↓
Business Analytics
        ↓
Excel Report / Power BI
```

---

## Main Features

The project includes:

- synthetic business data generation;
- Excel workbook upload;
- Excel structure validation;
- PostgreSQL raw data storage;
- automated Data Quality checks;
- clean data layer;
- ABC/XYZ product segmentation;
- sales KPI calculation;
- customer analysis;
- product analysis;
- channel analysis;
- manager performance analysis;
- promotion effectiveness analysis;
- BI-ready analytical marts;
- Power BI integration;
- downloadable Excel templates;
- downloadable sample datasets;
- Data Quality issue browser;
- downloadable Excel analytics report;
- Docker-based deployment.

---

# Technology Stack

- Python 3.12
- Pandas
- NumPy
- PostgreSQL 16
- SQLAlchemy
- psycopg2
- FastAPI
- Uvicorn
- Jinja2
- openpyxl
- Docker
- Docker Compose
- pgAdmin
- Power BI
- pytest

---

# Architecture

```text
                    ┌─────────────────────┐
                    │   Data Sources      │
                    │                     │
                    │ Synthetic / Excel   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      raw schema     │
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
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
       ┌──────────────────┐       ┌──────────────────┐
       │ Excel Reporting  │       │     Power BI     │
       └──────────────────┘       └──────────────────┘
```

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
            ├── __init__.py
            ├── main.py
            │
            └── templates/
                ├── index.html
                ├── result.html
                └── issues.html
```

---

# PostgreSQL Data Layers

The project separates data into three PostgreSQL schemas.

## raw

Stores source data without business cleaning.

Tables:

```text
raw.products
raw.customers
raw.sales
raw.promotions
```

The raw layer preserves the source dataset so Data Quality issues remain traceable.

---

## clean

Stores validated datasets after Data Quality rules are applied.

Tables:

```text
clean.products
clean.customers
clean.sales
clean.promotions
```

---

## analytics

Stores analytical tables, KPI outputs, Data Quality results, and BI-ready views.

Main objects include:

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

The project automatically checks multiple Data Quality dimensions.

## Completeness

Example:

```text
Missing barcode
Missing category
Missing required values
```

SQL example:

```sql
SELECT *
FROM raw.products
WHERE barcode IS NULL;
```

---

## Uniqueness

Example:

```text
Duplicate barcode
Duplicate sales records
```

SQL example:

```sql
SELECT
    barcode,
    COUNT(*)
FROM raw.products
WHERE barcode IS NOT NULL
GROUP BY barcode
HAVING COUNT(*) > 1;
```

---

## Validity

Example:

```text
Negative quantity
Invalid sales price
Sales price below allowed business rule
```

---

## Referential Integrity

Example:

A sales record references a product that does not exist.

```sql
SELECT s.*
FROM raw.sales s
LEFT JOIN raw.products p
    ON s.product_id = p.product_id
WHERE p.product_id IS NULL;
```

---

# Demo Dataset

The default synthetic dataset contains approximately:

```text
Products:     500
Customers:    500
Sales:     30,003
Promotions:    40
```

Intentional Data Quality problems are inserted into the generated data so the validation pipeline can detect and report them.

Example issues include:

- missing barcodes;
- duplicate barcodes;
- missing categories;
- invalid product prices;
- negative quantity;
- invalid unit price;
- unknown product IDs;
- unknown customer IDs;
- duplicate sales records.

A typical pipeline run detects:

```text
Data Quality Issues: 105
Data Quality Score:   99.66%
```

The score is a simplified portfolio metric and should not be interpreted as a universal production-grade Data Quality methodology.

---

# Excel Upload

The project includes a FastAPI web interface for uploading business datasets.

Open:

```text
http://localhost:8002
```

The interface supports:

```text
Download Excel Template
Download Sample Excel
Upload & Run Analysis
```

---

## Required Excel Sheets

An uploaded workbook must contain:

```text
products
customers
sales
promotions
```

The column names must match the current PostgreSQL `raw` table structure.

---

## Excel Processing Flow

```text
Excel Upload
    ↓
Workbook Validation
    ↓
Sheet Validation
    ↓
Column Validation
    ↓
Load to raw schema
    ↓
Data Quality Checks
    ↓
Clean Layer
    ↓
ABC/XYZ
    ↓
Business Analytics
    ↓
Reporting
```

---

# Excel Template

The application can generate an empty Excel workbook containing the exact column structure required by the database.

Use:

```text
Download Excel Template
```

The generated file is:

```text
sales_data_template.xlsx
```

---

# Sample Excel Dataset

The application can export the current PostgreSQL raw dataset to Excel.

Use:

```text
Download Sample Excel
```

The generated file is:

```text
sales_data_sample.xlsx
```

This file can be uploaded back into the application to test the complete Excel ingestion pipeline.

---

# Data Quality Issues Page

After the pipeline completes, the user can open:

```text
View Data Quality Issues
```

The page displays:

```text
Check
Table
Issue Type
Row Key
Detail
```

This makes the detected data problems visible without directly querying PostgreSQL.

---

# Excel Analytics Report

After analysis, the system can generate:

```text
data_quality_report.xlsx
```

The report contains multiple sheets:

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

The exported worksheets include:

- frozen headers;
- filters;
- automatically adjusted column widths.

---

# ABC Analysis

ABC analysis classifies products by cumulative revenue contribution.

Default thresholds:

```text
A: first 80% of cumulative revenue
B: next 15%
C: remaining 5%
```

The thresholds are configurable through environment variables:

```env
ABC_A_THRESHOLD=0.80
ABC_B_THRESHOLD=0.95
```

---

# XYZ Analysis

XYZ analysis measures demand stability using the coefficient of variation.

```text
CV = Standard Deviation / Mean
```

Default thresholds:

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

# Business KPIs

The analytics pipeline calculates:

```text
Revenue
Orders
Customers
Products Sold
Average Order Value
Gross Profit
Gross Margin %
```

Basic formulas:

```text
Revenue =
Quantity × Unit Price
```

```text
Gross Profit =
Revenue - Cost
```

```text
Margin % =
Gross Profit / Revenue × 100
```

```text
Average Order Value =
Revenue / Number of Orders
```

---

# Promotion Analysis

The project compares the promotion period with an equal-duration baseline period before the campaign.

Metrics include:

```text
Revenue Before
Revenue During

Quantity Before
Quantity During

Revenue Uplift %
Quantity Uplift %
```

Example:

```text
Revenue before = 1,000,000
Revenue during = 1,250,000

Revenue uplift = 25%
```

In a production environment, additional factors should also be considered:

- gross profit;
- margin;
- seasonality;
- customer segmentation;
- control groups.

---

# Power BI

The PostgreSQL analytics layer is designed for direct Power BI consumption.

Recommended dashboard pages:

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

```bash
cd sales_data_quality
```

---

## 2. Create the environment file

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

# Start the Services

```bash
docker compose up -d db pgadmin web
```

Check containers:

```bash
docker compose ps
```

---

# Web Interface

Open:

```text
http://localhost:8002
```

---

# pgAdmin

Open:

```text
http://localhost:5050
```

Default login from `.env`:

```text
admin@example.com
admin
```

When connecting from pgAdmin running inside Docker:

```text
Host: db
Port: 5432
Database: sales_quality
User: postgres
Password: postgres
```

---

# External PostgreSQL Connection

For DBeaver or Power BI on the Windows host:

```text
Host: localhost
Port: 55432
Database: sales_quality
User: postgres
Password: postgres
```

---

# Run the Demo Pipeline

The original synthetic-data workflow remains available.

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

---

# Run Tests

```bash
docker compose run --rm analytics pytest -q
```

Current test coverage includes:

- revenue calculation;
- margin calculation;
- duplicate detection logic.

---

# Excel Upload Pipeline

Excel uploads use a separate processing flow:

```text
Excel
↓
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

This intentionally skips:

```text
generate_data.py
load_raw.py
```

because uploaded data is already loaded into the PostgreSQL raw layer.

---

# Example SQL Queries

## Total Revenue

```sql
SELECT
    SUM(revenue)
FROM clean.sales;
```

---

## Number of Orders

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

# Why This Project Was Built

This project demonstrates practical skills required for analytics and Data Quality roles:

- working with business data;
- SQL analysis;
- Python/Pandas data processing;
- Data Quality validation;
- ERP-style data relationships;
- sales analysis;
- product segmentation;
- promotion analysis;
- business KPI calculation;
- Excel ingestion;
- automated reporting;
- PostgreSQL data modeling;
- Docker deployment;
- Power BI integration.

---

# Portfolio Value

The project is designed to demonstrate the ability to work across the complete analytics lifecycle:

```text
Source Data
→ Data Ingestion
→ Validation
→ Cleaning
→ Data Modeling
→ Business Analysis
→ Reporting
→ BI
```

It also demonstrates the ability to combine software engineering skills with business analytics and Data Quality practices.

---

# Author

**Khachatur Khachatryan**

GitHub:

```text
https://github.com/khachatryan1988
```

Project repository:

```text
https://github.com/khachatryan1988/sales_data_quality
```