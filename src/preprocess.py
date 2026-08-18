import pandas as pd

INPUT_FILE = "data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv"
OUTPUT_FILE = "data/processed/clean_churn_data.csv"

# Load raw data
df = pd.read_csv(INPUT_FILE)

print("Original shape:", df.shape)

# Convert TotalCharges from text to numeric
df["TotalCharges"] = pd.to_numeric(
    df["TotalCharges"].str.strip(),
    errors="coerce"
)

# Check missing TotalCharges
missing_total_charges = df["TotalCharges"].isnull().sum()
print("Missing TotalCharges:", missing_total_charges)

# Customers with tenure = 0 have no accumulated charges
df.loc[df["tenure"] == 0, "TotalCharges"] = 0

# Remove customer ID because it is only an identifier
df = df.drop(columns=["customerID"])

# Convert target variable
df["Churn"] = df["Churn"].map({
    "No": 0,
    "Yes": 1
})

# Check and remove duplicate records
duplicates = df.duplicated().sum()
print("Duplicates found:", duplicates)

df = df.drop_duplicates()

print("Duplicates after cleaning:", df.duplicated().sum())

# Save cleaned dataset
df.to_csv(OUTPUT_FILE, index=False)

print("Cleaned shape:", df.shape)
print("Cleaned data saved to:", OUTPUT_FILE)