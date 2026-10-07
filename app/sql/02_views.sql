-- Create reusable business reporting views in the analytics schema.


-- ============================================================
-- Sales by category
-- ============================================================

CREATE OR REPLACE VIEW analytics.v_sales_by_category AS
SELECT
    p.category,

    ROUND(
        SUM(s.revenue)::numeric,
        2
    ) AS revenue,

    SUM(s.quantity) AS quantity,

    COUNT(
        DISTINCT s.order_id
    ) AS orders

FROM clean.sales s

JOIN clean.products p
    ON s.product_id = p.product_id

GROUP BY
    p.category;


-- ============================================================
-- Sales by brand
-- ============================================================

CREATE OR REPLACE VIEW analytics.v_sales_by_brand AS
SELECT
    p.brand,

    ROUND(
        SUM(s.revenue)::numeric,
        2
    ) AS revenue,

    SUM(s.quantity) AS quantity,

    COUNT(
        DISTINCT s.order_id
    ) AS orders

FROM clean.sales s

JOIN clean.products p
    ON s.product_id = p.product_id

GROUP BY
    p.brand;


-- ============================================================
-- Monthly sales
-- ============================================================

CREATE OR REPLACE VIEW analytics.v_monthly_sales AS
SELECT
    DATE_TRUNC(
        'month',
        order_date
    )::date AS month,

    ROUND(
        SUM(revenue)::numeric,
        2
    ) AS revenue,

    COUNT(
        DISTINCT order_id
    ) AS orders,

    SUM(quantity) AS quantity

FROM clean.sales

GROUP BY
    DATE_TRUNC(
        'month',
        order_date
    )::date

ORDER BY
    month;