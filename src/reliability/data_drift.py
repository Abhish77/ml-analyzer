import pandas as pd
import numpy as np


def calculate_psi(reference, current, bins=10):
    """
    Calculate Population Stability Index (PSI).
    """

    reference = pd.Series(reference).dropna()
    current = pd.Series(current).dropna()

    breakpoints = np.linspace(0, 100, bins + 1)

    reference_percentiles = np.percentile(
        reference,
        breakpoints
    )

    reference_percentiles = np.unique(
        reference_percentiles
    )

    if len(reference_percentiles) < 3:
        return 0.0

    reference_bins = pd.cut(
        reference,
        bins=reference_percentiles,
        include_lowest=True
    )

    current_bins = pd.cut(
        current,
        bins=reference_percentiles,
        include_lowest=True
    )

    reference_counts = (
        reference_bins
        .value_counts(normalize=True)
        .sort_index()
    )

    current_counts = (
        current_bins
        .value_counts(normalize=True)
        .reindex(
            reference_counts.index,
            fill_value=0
        )
    )

    epsilon = 0.0001

    reference_counts = reference_counts.clip(
        lower=epsilon
    )

    current_counts = current_counts.clip(
        lower=epsilon
    )

    psi = (
        (current_counts - reference_counts)
        * np.log(
            current_counts / reference_counts
        )
    ).sum()

    return float(psi)


def interpret_psi(psi):

    if psi < 0.10:
        return "Stable"

    elif psi < 0.25:
        return "Warning"

    else:
        return "Significant Drift"


def detect_drift(reference_df, current_df):

    numerical_columns = reference_df.select_dtypes(
        include=["int64", "float64"]
    ).columns

    results = {}

    for column in numerical_columns:

        if column == "Churn":
            continue

        psi = calculate_psi(
            reference_df[column],
            current_df[column]
        )

        results[column] = {
            "psi": round(psi, 4),
            "status": interpret_psi(psi)
        }

    return results


if __name__ == "__main__":

    REFERENCE_FILE = (
        "data/processed/clean_churn_data.csv"
    )

    PRODUCTION_FILE = (
        "data/processed/simulated_production_data.csv"
    )

    reference_df = pd.read_csv(
        REFERENCE_FILE
    )

    production_df = pd.read_csv(
        PRODUCTION_FILE
    )

    results = detect_drift(
        reference_df,
        production_df
    )

    print("\n--- PRODUCTION DATA DRIFT REPORT ---")

    for feature, result in results.items():

        print(
            f"{feature}: "
            f"PSI={result['psi']} "
            f"Status={result['status']}"
        )