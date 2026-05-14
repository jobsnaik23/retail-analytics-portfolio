# Multi-Channel Retail Analytics & Predictive CLV Engine

## 📊 Executive Summary
This end-to-end data analytics project builds a retail intelligence ecosystem. By extracting over 1 million transactional logs, cleaning the data pipeline via Python, and structuring historical and predictive customer models, this workspace delivers concrete commercial strategies. 

The project operates entirely in English, simulating an international retail context (e.g., Carrefour/Delhaize) within the Belgian commercial market.

---

## 🚀 Business Capabilities Delivered

### 1. Data Analysis & Loyalty Tracking
* **Action:** Implemented a localized RFM (Recency, Frequency, Monetary) segmentation model to categorize customers into behavioral tiers (Champions, At-Risk, New Customers, Lost).
* **Loyalty Focus:** Isolated "Bonus Card" holders from anonymous shoppers using binary tracking layers to measure transactional frequencies and brand dependency.

### 2. Customer Journey Optimization
* **Action:** Simulated and analyzed customer touchpoints across Web, Mobile App, and In-Store channels.
* **Insight:** Discovered which interface routes process the highest volume of distinct transaction completions.

### 3. Predictive Modeling (Customer Lifetime Value)
* **Action:** Trained Beta-Geometric (BG/NBD) and Gamma-Gamma statistical algorithms using the `lifetimes` framework.
* **Output:** Quantified expected purchase counts over a 90-day horizon and projected continuous 12-Month Customer Lifetime Value (CLV) to anticipate future consumer value.

---

## 📈 Strategic Business Recommendations (Actionable Insights)
* **At-Risk Target Campaign:** Bonus Card holders flagged in the "At Risk" RFM segment with high predictive 12-month CLV scores should receive automated, localized mobile application coupons exactly 75 days after their last transaction to mitigate churn.
* **Cross-Channel Onboarding:** Shoppers interacting solely via "In-Store" channels yield a lower overall value. Marketing should leverage in-store point-of-sale signs promoting a €5 registration bonus for the Mobile App to trigger multi-channel migration.

---

## 🛠️ Data Infrastructure & Repository Architecture
```text
retail-analytics-portfolio/
├── data/
│   └── powerbi_ready.csv         # Standardized flat database export
├── scripts/
│   ├── local_pipeline.py         # Data engineering, cleaning, and channel simulation
│   ├── rfm_analysis.py           # Historical RFM quintile segmentation engine
│   ├── predictive_clv.py         # Machine learning BG/NBD & Gamma-Gamma model training
│   └── export_powerbi_file.py    # High-performance flat data structuring pipeline
├── retail_performance_cockpit.pbix # Completed Power BI Desktop dashboard file
└── README.md                     # Executive overview and technical methodology
```