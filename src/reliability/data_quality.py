import pandas as pd


def check_data_quality(df):
    """Check the quality of a dataset."""

    results = {}

    # 1. Missing values
    missing_values = int(df.isnull().sum().sum())
    results["missing_values"] = missing_values

    # 2. Duplicate rows
    duplicate_rows = int(df.duplicated().sum())
    results["duplicate_rows"] = duplicate_rows

    # 3. Empty string values
    empty_values = int(
        df.select_dtypes(include=["object"])
        .apply(lambda col: col.str.strip().eq("").sum())
        .sum()
    )
    results["empty_values"] = empty_values

    # 4. Number of rows
    results["rows"] = len(df)

    # 5. Number of columns
    results["columns"] = len(df.columns)

    # 6. Calculate quality score
    score = 100

    if missing_values > 0:
        score -= 20

    if duplicate_rows > 0:
        score -= 15

    if empty_values > 0:
        score -= 10

    score = max(score, 0)

    results["quality_score"] = score

    # 7. Determine status
    if score >= 90:
        status = "Healthy"
    elif score >= 70:
        status = "Warning"
    else:
        status = "Critical"

    results["status"] = status

    return results


if __name__ == "__main__":

    DATA_FILE = "data/processed/clean_churn_data.csv"

    df = pd.read_csv(DATA_FILE)

    results = check_data_quality(df)

    print("\n--- DATA QUALITY REPORT ---")

    print("Rows:", results["rows"])
    print("Columns:", results["columns"])
    print("Missing values:", results["missing_values"])
    print("Duplicate rows:", results["duplicate_rows"])
    print("Empty values:", results["empty_values"])

    print("\nQuality Score:", results["quality_score"], "/ 100")
    print("Status:", results["status"])