import pandas as pd
import numpy as np

INPUT_FILE = "data/processed/clean_churn_data.csv"
OUTPUT_FILE = "data/processed/simulated_production_data.csv"

# Load clean data
df = pd.read_csv(INPUT_FILE)

# Make a copy for simulated production data
production_df = df.copy()

# Simulate customer behavior changes
production_df["MonthlyCharges"] = (
    production_df["MonthlyCharges"] * 1.30
)

production_df["TotalCharges"] = (
    production_df["TotalCharges"] * 1.25
)

# Add small random variation
np.random.seed(42)

production_df["MonthlyCharges"] += np.random.normal(
    0,
    5,
    len(production_df)
)

production_df["TotalCharges"] += np.random.normal(
    0,
    50,
    len(production_df)
)

# Save simulated production data
production_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Simulated production data created.")
print("Saved to:", OUTPUT_FILE)