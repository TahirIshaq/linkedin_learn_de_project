{{ config(materialized='table') }}

WITH
    customers AS (SELECT * FROM {{ ref("stg_customers") }}),
    orders AS (SELECT * FROM {{ ref("stg_orders") }}),
    customer_orders AS (
        SELECT
            c.customer_id,
            c.email,
            c.country,
            c.city,
            MIN(o.order_approved_at) AS first_order_date,
            MAX(o.order_approved_at) AS most_recent_date,
            COUNT(o.order_id) AS number_of_orders
        FROM
            orders o
            INNER JOIN customers c
            ON o.customer_id=c.customer_id
        GROUP BY
            c.customer_id,
            c.email,
            c.country,
            c.city
    )
    SELECT
        *
    FROM
        customer_orders