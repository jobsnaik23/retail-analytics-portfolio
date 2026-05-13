import os
import sqlite3
import pandas as pd

# 1. Locate the database file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "retail_local.db")

conn = sqlite3.connect(db_path)

# 2. Query a small sample (the top 5 rows) of your consolidated master dataset
query = "SELECT * FROM master_dashboard_dataset LIMIT 5;"
df_sample = pd.read_sql_query(query, conn)
conn.close()

# 3. Print the sample to the terminal screen
print("\n--- MASTER DASHBOARD DATASET PREVIEW ---")
print(df_sample.to_string())