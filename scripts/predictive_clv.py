import os
import sqlite3
import numpy as np
import pandas as pd
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data

# 1. Dynamically locate the project root folder (moves up 1 level from 'scripts')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, "retail_local.db")

print(f"Connecting to database at: {db_path}")
conn = sqlite3.connect(db_path)

# 2. Extract transaction logs for loyalty program ("Bonus Card") holders
query = """
SELECT 
    bonus_card_id, 
    transaction_timestamp, 
    (quantity_purchased * unit_price_eur) as monetary_value
FROM transactions_cleaned 
WHERE bonus_card_id IS NOT NULL
"""
df = pd.read_sql_query(query, conn)
conn.close()

# 3. Standardize and parse continuous timestamps
df['transaction_timestamp'] = pd.to_datetime(df['transaction_timestamp'])

# 4. Transform individual transaction rows into aggregate user matrices (RFM)
print("Transforming transactions into customer-level RFM metrics...")
rfm_summary = summary_data_from_transaction_data(
    df, 
    customer_id_col='bonus_card_id', 
    datetime_col='transaction_timestamp', 
    monetary_value_col='monetary_value',
    observation_period_end=df['transaction_timestamp'].max()
)

# Filter out zero-frequency customers (one-time buyers) to fulfill mathematical Gamma-Gamma limits
rfm_summary = rfm_summary[rfm_summary['frequency'] > 0]

# 5. Fit the BG/NBD model to predict future purchase frequency
print("Training BG/NBD probability distribution curves for frequency...")
bgf = BetaGeoFitter(penalizer_coef=0.01)
bgf.fit(rfm_summary['frequency'], rfm_summary['recency'], rfm_summary['T'])

# Calculate expected purchases over the next 90 days to anticipate immediate consumer needs
rfm_summary['predicted_purchases_90_days'] = bgf.conditional_expected_number_of_purchases_up_to_time(
    90, rfm_summary['frequency'], rfm_summary['recency'], rfm_summary['T']
)

# 6. Fit the Gamma-Gamma model to isolate average transactional values
print("Training Gamma-Gamma curves to calculate expected ticket spend...")
ggf = GammaGammaFitter(penalizer_coef=0.01)
ggf.fit(rfm_summary['frequency'], rfm_summary['monetary_value'])

rfm_summary['expected_avg_spend'] = ggf.conditional_expected_average_profit(
    rfm_summary['frequency'],
    rfm_summary['monetary_value']
)

# 7. Generate final continuous 12-Month Predictive Customer Lifetime Value (CLV)
# Assumes standard 1% monthly financial discount rate for present value calculations
print("Computing final continuous 12-Month Customer Lifetime Value (CLV)...")
rfm_summary['predictive_clv_12m'] = ggf.customer_lifetime_value(
    bgf,
    rfm_summary['frequency'],
    rfm_summary['recency'],
    rfm_summary['T'],
    rfm_summary['monetary_value'],
    time=12,             # Forecast horizon in months
    discount_rate=0.01   # Monthly discount rate
)

# 8. Commit data back into a fresh standalone table within local storage
print("Writing predictions back to local storage file...")
output_df = rfm_summary[['predicted_purchases_90_days', 'expected_avg_spend', 'predictive_clv_12m']].reset_index()

conn = sqlite3.connect(db_path)
output_df.to_sql("customer_predictive_clv", conn, if_exists="replace", index=False)
conn.close()

print("\n[SUCCESS] Predictive CLV Layer successfully completed and saved!")
print(output_df[['predicted_purchases_90_days', 'predictive_clv_12m']].describe().round(2))