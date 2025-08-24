{{ 
    config(
        materialized='incremental', 
        file_format='iceberg',
        incremental_strategy='insert_overwrite',
        partition_by=['data_date']
    ) 
}}

WITH cdp_tbl_cdp_balance_report_byday
AS(
    SELECT tf_sourcing_at
      , id
      , report_date
      , contract_number
      , customer_cif
      , is_intermediary
      , dao_code
      , original_branch_code
      , transfer_branch_code
      , currency
      , category_code
      , product_code
      , issue_date
      , effective_date
      , maturity_date
      , term
      , contract_interest_rate
      , holding_days
      , yield_rate
      , interest_rate_type
      , interest_calculation_basis
      , holiday_handling_mechanism
      , issue_lot_code
      , certificate_number
      , sales_channel
      , created_by
      , approved_by
      , original_balance
      , face_amount
      , quantity
      , first_interest_payment_date
      , last_interest_payment_date
      , next_interest_payment_date
      , interest_payment_frequency
      , sell_date
      , expected_holding_days
      , purchase_price
      , daily_interest_accrual
      , cumulative_interest_accrual_from_purchase
      , cumulative_interest_accrual_from_last_payment
      , az_code
      , t24_old_ref
      , created_at
      , created_by_user
      , hh_company
      , customer_cif
    FROM {{ source('eod', 'cdp_tbl_cdp_balance_report_byday__mnp') }} -- sysdate-1
    WHERE year = '2025' and month = '07' and day = '21'
),

t24_customer
AS(
    SELECT customer_code
      , segment
    FROM {{ source('eod', 't24_customer__s2') }}
    WHERE tf_updated_at > CAST('2025-05-30' AS date) -- t24lwd
    AND tf_created_at <=  CAST('2025-05-30' AS date)
)

SELECT a.tf_sourcing_at,
    current_timestamp as tf_etl_at,
    CAST('{{var('datadate')}}' AS DATE) AS data_date,
    a.id,
    a.report_date,
    a.contract_number,
    a.customer_cif,
    a.is_intermediary,
    a.dao_code,
    a.original_branch_code,
    a.transfer_branch_code,
    a.currency,
    a.category_code,
    a.product_code,
    a.issue_date,
    a.effective_date,
    a.maturity_date,
    a.term,
    a.contract_interest_rate,
    a.holding_days,
    a.yield_rate,
    a.interest_rate_type,
    a.interest_calculation_basis,
    a.holiday_handling_mechanism,
    a.issue_lot_code,
    a.certificate_number,
    a.sales_channel,
    a.created_by,
    a.approved_by,
    a.original_balance,
    a.face_amount,
    a.quantity,
    a.first_interest_payment_date,
    a.last_interest_payment_date,
    a.next_interest_payment_date,
    a.interest_payment_frequency,
    a.sell_date,
    a.expected_holding_days,
    a.purchase_price,
    a.daily_interest_accrual,
    a.cumulative_interest_accrual_from_purchase,
    a.cumulative_interest_accrual_from_last_payment,
    a.az_code,
    a.t24_old_ref,
    a.created_at,
    a.created_by_user,
    a.hh_company,
    b.segment
FROM cdp_tbl_cdp_balance_report_byday a
LEFT JOIN t24_customer b
ON a.customer_cif = b.customer_code