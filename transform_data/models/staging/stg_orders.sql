-- Set the output of the model
{{ config(materialized='view') }}

-- The columns data types should be changed here if required.
SELECT
    order_id,
    customer_id,
    status as order_status,
    order_approved_at,
    order_delivered_at
FROM {{ source("raw_data", "orders") }}