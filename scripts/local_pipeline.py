import pandas as pd
import sqlite3
import numpy as np
import os

# Dynamically locate the root directory of your project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, "data", "raw_retail_transactions.csv")
db_path = os.path.join(BASE_DIR, "retail_local.db")

# 1. Load the raw downloaded dataset
print("Loading raw CSV data...")
df = pd.read_csv(csv_path)

# 2. Establish a local SQLite Database file
conn = sqlite3.connect(db_path)

# 3. Stream the raw data into your local database
df.to_sql("transactions_raw", conn, if_exists="replace", index=False)

# 4. Run your SQL Cleaning & Multi-Channel logic locally
local_sql_query = """
CREATE TABLE IF NOT EXISTS transactions_cleaned AS
SELECT
  CAST(Invoice AS TEXT) AS transaction_id,
  CAST(StockCode AS TEXT) AS product_sku,
  TRIM(Description) AS product_name,
  CAST(Quantity AS INTEGER) AS quantity_purchased,
  InvoiceDate AS transaction_timestamp,
  CAST(Price AS REAL) AS unit_price_eur,
  CAST([Customer ID] AS TEXT) AS bonus_card_id,
  CASE WHEN [Customer ID] IS NOT NULL THEN 1 ELSE 0 END AS is_bonus_card_holder,
  -- Deterministic split for channel simulation
  CASE WHEN ABS(HEX(Invoice)) % 3 = 0 THEN 'Web'
       WHEN ABS(HEX(Invoice)) % 3 = 1 THEN 'Mobile App'
       ELSE 'In-Store' END AS purchase_touchpoint
FROM transactions_raw
WHERE Description IS NOT NULL AND Price > 0 AND Quantity > 0;
"""

print("Executing local database transformations...")
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS transactions_cleaned;")
cursor.execute(local_sql_query)
conn.commit()

print("Local database setup complete! Your 'retail_local.db' file is ready.")
conn.close()