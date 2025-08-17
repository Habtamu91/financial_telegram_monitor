WITH message_risks AS (
  SELECT
    message_id,
    CASE 
      WHEN contains_urgent_language THEN 0.7 
      WHEN has_unverified_claims THEN 0.9
      ELSE 0.1
    END AS risk_score
  FROM {{ ref('stg_financial_messages') }}
)