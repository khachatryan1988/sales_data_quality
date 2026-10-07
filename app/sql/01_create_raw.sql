-- Create the raw, clean, and analytics schemas used by the project.
-- Rebuild the raw source tables before loading a new synthetic dataset.

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS clean;
CREATE SCHEMA IF NOT EXISTS analytics;

DROP TABLE IF EXISTS raw.sales;
DROP TABLE IF EXISTS raw.promotions;
DROP TABLE IF EXISTS raw.products;
DROP TABLE IF EXISTS raw.customers;

CREATE TABLE raw.products (
    product_id BIGINT,
    sku TEXT,
    barcode TEXT,
    product_name TEXT,
    brand TEXT,
    category TEXT,
    cost_price NUMERIC(14,2),
    sale_price NUMERIC(14,2)
);

CREATE TABLE raw.customers (
    customer_id BIGINT,
    customer_name TEXT,
    customer_type TEXT,
    city TEXT,
    registration_date DATE
);

CREATE TABLE raw.sales (
    sales_line_id BIGINT,
    order_id BIGINT,
    order_date DATE,
    customer_id BIGINT,
    product_id BIGINT,
    quantity NUMERIC(14,2),
    unit_price NUMERIC(14,2),
    discount NUMERIC(8,4),
    revenue NUMERIC(14,2),
    channel TEXT,
    manager TEXT
);

CREATE TABLE raw.promotions (
    promotion_id BIGINT,
    product_id BIGINT,
    start_date DATE,
    end_date DATE,
    discount_percent NUMERIC(8,2),
    campaign_name TEXT
);
