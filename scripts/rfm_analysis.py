import os
import pandas as pd
import sqlite3

# 1. Dynamically find the project root folder (moves up 1 level from 'scripts')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "retail_local.db")

print(f"Connecting to database at: {db_path}")
conn = sqlite3.connect(db_path)

# 2. Pull cleaned transactional logs
query = """
SELECT 
    bonus_card_id, 
    transaction_timestamp, 
    quantity_purchased, 
    unit_price_eur 
FROM transactions_cleaned 
WHERE bonus_card_id IS NOT NULL
"""
df = pd.read_sql_query(query, conn)
conn.close()

# 3. Calculate Total Spent per transaction line
df['total_revenue'] = df['quantity_purchased'] * df['unit_price_eur']

# 4. Standardize timestamps
df['transaction_timestamp'] = pd.to_datetime(df['transaction_timestamp'])
snapshot_date = df['transaction_timestamp'].max() + pd.Timedelta(days=1)

# 5. Group data by customer (Calculate Recency, Frequency, Monetary)
print("Calculating baseline RFM variables per unique customer...")
rfm = df.groupby('bonus_card_id').agg({
    'transaction_timestamp': lambda x: (snapshot_date - x.max()).days, # Recency
    'bonus_card_id': 'count',                                         # Frequency
    'total_revenue': 'sum'                                            # Monetary
})

# 6. Standardize column identifiers
rfm.rename(columns={
    'transaction_timestamp': 'recency',
    'bonus_card_id': 'frequency',
    'total_revenue': 'monetary'
}, inplace=True)

# 7. Generate rank scores from 1 to 5 using quintiles
# We use rankings to deal with duplicate transaction counts seamlessly
rfm['R'] = pd.qcut(rfm['recency'].rank(method='first'), 5, labels=[5, 4, 3, 2, 1]) # Low recency days = high score
rfm['F'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
rfm['M'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])

# 8. Map behavioral categories based on structural scores
def assign_segment(row):
    score = f"{row['R']}{row['F']}{row['M']}"
    if score in ['555', '554', '545', '455']: return 'Champions (VIP)'
    elif row['R'] >= 4 and row['F'] >= 3:      return 'Loyal Customers'
    elif row['R'] >= 4 and row['F'] <= 2:      return 'Recent/New Customers'
    elif row['R'] <= 2 and row['F'] >= 4:      return 'At Risk / Can\'t Lose Them'
    elif row['R'] <= 2 and row['F'] <= 2:      return 'Lost / Inactive'
    else:                                      return 'Regular Shoppers'

rfm['customer_segment'] = rfm.apply(assign_segment, axis=1)

# 9. Write outputs back into your local database
print("Saving segmented behavioral cohorts back to database...")
conn = sqlite3.connect(db_path)
rfm.to_sql("customer_rfm_segments", conn, if_exists="replace")
conn.close()

print("\nRFM Customer Segmentation successfully executed!")
print(rfm['customer_segment'].value_counts())