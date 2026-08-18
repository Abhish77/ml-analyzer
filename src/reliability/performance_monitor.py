import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


DATA_FILE = "data/processed/clean_churn_data.csv"
MODEL_FILE = "models/churn_model.pkl"


# Baseline performance from our trained model
BASELINE = {
    "accuracy": 0.7722,
    "precision": 0.5949,
    "recall": 0.4382,
    "f1": 0.5046
}


def evaluate_model(model, X, y):

    predictions = model.predict(X)

    metrics = {
        "accuracy": accuracy_score(y, predictions),
        "precision": precision_score(
            y,
            predictions,
            zero_division=0
        ),
        "recall": recall_score(
            y,
            predictions,
            zero_division=0
        ),
        "f1": f1_score(
            y,
            predictions,
            zero_division=0
        )
    }

    return metrics


def calculate_performance_status(metrics):

    # Calculate average relative degradation
    degradation = []

    for metric in BASELINE:

        baseline_value = BASELINE[metric]
        current_value = metrics[metric]

        if baseline_value > 0:

            change = (
                baseline_value - current_value
            ) / baseline_value

            degradation.append(change)

    average_degradation = sum(degradation) / len(degradation)

    if average_degradation < 0.05:
        status = "Healthy"

    elif average_degradation < 0.15:
        status = "Warning"

    else:
        status = "Critical"

    return average_degradation, status


if __name__ == "__main__":

    print("\n--- MODEL PERFORMANCE MONITOR ---")

    # Load data
    df = pd.read_csv(DATA_FILE)

    X = df.drop(columns=["Churn"])
    y = df["Churn"]

    # Same split used during training
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    # Load saved model
    model = joblib.load(MODEL_FILE)

    # Evaluate
    metrics = evaluate_model(
        model,
        X_test,
        y_test
    )

    print("\nCurrent Performance:")

    for metric, value in metrics.items():

        print(
            f"{metric.capitalize():10}: "
            f"{value:.4f}"
        )

    # Compare with baseline
    degradation, status = calculate_performance_status(
        metrics
    )

    print(
        f"\nAverage degradation: "
        f"{degradation * 100:.2f}%"
    )

    print("Performance status:", status)