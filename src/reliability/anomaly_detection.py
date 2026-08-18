import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


DATA_FILE = "data/processed/clean_churn_data.csv"


def detect_anomalies(df):
    """
    Detect unusual customer records using Isolation Forest.
    """

    # Select numerical features
    numerical_columns = [
        "SeniorCitizen",
        "tenure",
        "MonthlyCharges",
        "TotalCharges"
    ]

    data = df[numerical_columns].copy()

    # Scale numerical features
    scaler = StandardScaler()

    scaled_data = scaler.fit_transform(data)

    # Create anomaly detector
    detector = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42
    )

    # Predict
    predictions = detector.fit_predict(scaled_data)

    # -1 = anomaly
    #  1 = normal
    df = df.copy()

    df["anomaly"] = predictions

    anomaly_count = (predictions == -1).sum()

    total_records = len(df)

    anomaly_percentage = (
        anomaly_count / total_records
    ) * 100

    return df, anomaly_count, anomaly_percentage


if __name__ == "__main__":

    df = pd.read_csv(DATA_FILE)

    results, anomaly_count, anomaly_percentage = (
        detect_anomalies(df)
    )

    print("\n--- ANOMALY DETECTION REPORT ---")

    print("Total records:", len(results))

    print("Anomalies detected:", anomaly_count)

    print(
        f"Anomaly percentage: "
        f"{anomaly_percentage:.2f}%"
    )

    print("\nSample anomalies:")

    print(
        results[
            results["anomaly"] == -1
        ][
            [
                "tenure",
                "MonthlyCharges",
                "TotalCharges",
                "anomaly"
            ]
        ].head(10)
    )