# Sales & Data Quality Analytics System

End-to-end portfolio project demonstrating practical **data quality**, **SQL analytics**, **Python/Pandas**, **PostgreSQL**, **Docker**, and **Power BI** skills.

## Highlights

- Dockerized PostgreSQL, pgAdmin, and Python analytics pipeline
- Raw, clean, and analytics data layers
- Automated data quality checks
- Detailed data quality issue tracking
- ABC/XYZ product segmentation
- Sales, customer, channel, and manager analysis
- Promotion uplift analysis
- BI-ready analytical marts
- SQL views for common business reporting
- Automated unit tests

## Tech Stack

- Python
- Pandas
- NumPy
- PostgreSQL
- SQLAlchemy
- Docker Compose
- pgAdmin
- Pytest
- Power BI

## Business Questions

The project is designed to answer questions such as:

- Can the business trust its source data?
- Which products generate the most revenue?
- Which products have stable versus volatile demand?
- Which customers are the most valuable?
- Which channels and managers perform best?
- Which promotions create measurable uplift?

## Architecture

```text
Raw Data
   |
   v
Data Quality Checks
   |
   v
Clean Data Layer
   |
   v
Business Analytics + ABC/XYZ
   |
   v
Analytics Marts
   |
   v
Power BI
```

## Data Quality Checks

The pipeline checks:

- Completeness
- Uniqueness
- Validity
- Referential integrity

## Analytical Outputs

Main analytics objects include:

- KPI summary
- monthly sales
- product sales
- customer sales
- channel sales
- manager sales
- ABC/XYZ classification
- promotion performance
- data quality summary
- detailed data quality issues

## Running the Project

```powershell
docker compose up --build
```

## Running Tests

```powershell
docker compose run --rm analytics pytest -q
```

## Power BI

The `analytics` PostgreSQL schema contains BI-ready tables that can be connected directly from Power BI.

Recommended dashboard pages:

1. Executive Overview
2. Product & ABC/XYZ Analysis
3. Customer Analysis
4. Promotion Analysis
5. Data Quality
