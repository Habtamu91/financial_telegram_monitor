-- In dbt/models/marts/dim_regulatory_flags.sql
SELECT 
  message_id,
  text LIKE '%unregistered%' AS unregistered_offer,
  text LIKE '%insider%' AS insider_term
FROM {{ ref('stg_messages') }}