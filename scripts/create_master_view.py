import os
import sqlite3
import pandas as pd

# 1. Dynamically locate the project root folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "retail_local.db")

print(f"Connecting to database at: {db_path}")
conn = sqlite3.connect(db_path)

# 2. Write the Master SQL Join Query
# This merges transaction logs, RFM clusters, and CLV predictions into one dataset
master_sql_query = """
CREATE TABLE IF NOT EXISTS master_dashboard_dataset AS
SELECT
    t.transaction_id,
    t.product_sku,
    t.product_name,
    t.quantity_purchased,
    t.transaction_timestamp,
    t.unit_price_eur,
    (t.quantity_purchased * t.unit_price_eur) AS line_revenue_eur,
    t.bonus_card_id,
    t.is_bonus_card_holder,
    t.purchase_touchpoint,
    
    -- Historical Analytics Layer
    r.recency AS customer_recency_days,
    r.frequency AS customer_total_transactions,
    r.monetary AS customer_total_spend,
    r.customer_segment AS historical_rfm_segment,
    
    -- Forward-Looking Predictive Layer
    COALESCE(p.predicted_purchases_90_days, 0) AS predicted_purchases_next_90_days,
    COALESCE(p.expected_avg_spend, 0) AS predicted_avg_ticket_value,
    COALESCE(p.predictive_clv_12m, 0) AS predicted_customer_value_12m

FROM transactions_cleaned t
LEFT JOIN customer_rfm_segments r 
    ON t.bonus_card_id = r.bonus_card_id
LEFT JOIN customer_predictive_clv p 
    ON t.bonus_card_id = p.bonus_card_id;
"""

print("Executing master join script to unify retail tables...")
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS master_dashboard_dataset;")
cursor.execute(master_sql_query)
conn.commit()
conn.close()

print("[SUCCESS] Master view generated! Open your SQLite viewer to check: 'master_dashboard_dataset'")