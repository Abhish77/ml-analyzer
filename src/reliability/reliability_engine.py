import pandas as pd
import joblib

from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

from data_quality import check_data_quality
from data_drift import detect_drift
from anomaly_detection import detect_anomalies
from reliability_score import calculate_reliability_score


# ==================================================
# PROJECT PATH
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# ==================================================
# FILE PATHS
# ==================================================

REFERENCE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "clean_churn_data.csv"
)

PRODUCTION_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "simulated_production_data.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "churn_model.pkl"
)


# ==================================================
# BASELINE MODEL PERFORMANCE
# ==================================================

BASELINE = {
    "accuracy": 0.7722,
    "precision": 0.5949,
    "recall": 0.4382,
    "f1": 0.5046
}


# ==================================================
# DRIFT SCORE
# ==================================================

def calculate_drift_score(drift_results):

    psis = [
        result["psi"]
        for result in drift_results.values()
    ]

    if not psis:
        return 100

    max_psi = max(psis)

    if max_psi < 0.10:
        return 100

    elif max_psi < 0.25:
        return 70

    else:
        return 40


# ==================================================
# ANOMALY SCORE
# ==================================================

def calculate_anomaly_score(anomaly_percentage):

    if anomaly_percentage <= 2:
        return 100

    elif anomaly_percentage <= 5:
        return 90

    elif anomaly_percentage <= 10:
        return 70

    else:
        return 40


# ==================================================
# MODEL EVALUATION
# ==================================================

def evaluate_model(model, X, y):

    predictions = model.predict(X)

    metrics = {
        "accuracy": accuracy_score(
            y,
            predictions
        ),

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


# ==================================================
# PERFORMANCE SCORE
# ==================================================

def calculate_performance_score(metrics):

    degradations = []

    for metric in BASELINE:

        baseline_value = BASELINE[metric]
        current_value = metrics[metric]

        if baseline_value > 0:

            degradation = (
                baseline_value - current_value
            ) / baseline_value

            degradations.append(degradation)

    average_degradation = (
        sum(degradations)
        / len(degradations)
    )

    if average_degradation <= 0.05:

        score = 100

    elif average_degradation <= 0.15:

        score = 70

    else:

        score = 40

    return score, average_degradation


# ==================================================
# MAIN RELIABILITY ENGINE
# ==================================================

def run_reliability_engine():

    print("\n")
    print("=" * 60)
    print("          ML MODEL RELIABILITY ENGINE")
    print("=" * 60)


    # ==================================================
    # CHECK FILES
    # ==================================================

    print("\nChecking required files...")

    print(
        f"Reference data: {REFERENCE_FILE}"
    )

    print(
        f"Production data: {PRODUCTION_FILE}"
    )

    print(
        f"Model: {MODEL_FILE}"
    )


    if not REFERENCE_FILE.exists():

        raise FileNotFoundError(
            f"Reference dataset not found: {REFERENCE_FILE}"
        )


    if not PRODUCTION_FILE.exists():

        raise FileNotFoundError(
            f"Production dataset not found: {PRODUCTION_FILE}"
        )


    if not MODEL_FILE.exists():

        raise FileNotFoundError(
            f"Model not found: {MODEL_FILE}"
        )


    # ==================================================
    # LOAD DATA
    # ==================================================

    reference_df = pd.read_csv(
        REFERENCE_FILE
    )

    production_df = pd.read_csv(
        PRODUCTION_FILE
    )


    # ==================================================
    # 1. DATA QUALITY
    # ==================================================

    quality_results = check_data_quality(
        production_df
    )

    data_quality_score = (
        quality_results["quality_score"]
    )


    # ==================================================
    # 2. DATA DRIFT
    # ==================================================

    drift_results = detect_drift(
        reference_df,
        production_df
    )

    drift_score = calculate_drift_score(
        drift_results
    )


    # ==================================================
    # 3. ANOMALY DETECTION
    # ==================================================

    (
        _,
        anomaly_count,
        anomaly_percentage
    ) = detect_anomalies(
        production_df
    )

    anomaly_score = calculate_anomaly_score(
        anomaly_percentage
    )


    # ==================================================
    # 4. MODEL PERFORMANCE
    # ==================================================

    model = joblib.load(
        MODEL_FILE
    )

    X = production_df.drop(
        columns=["Churn"]
    )

    y = production_df["Churn"]

    performance_metrics = evaluate_model(
        model,
        X,
        y
    )

    (
        performance_score,
        degradation
    ) = calculate_performance_score(
        performance_metrics
    )


    # ==================================================
    # 5. OVERALL RELIABILITY SCORE
    # ==================================================

    (
        reliability_score,
        status
    ) = calculate_reliability_score(
        data_quality_score,
        drift_score,
        anomaly_score,
        performance_score
    )


    # ==================================================
    # CONSOLE REPORT
    # ==================================================

    print("\n--- DATA QUALITY ---")

    print(
        f"Score : {data_quality_score}/100"
    )

    print(
        f"Status: {quality_results['status']}"
    )


    print("\n--- DATA DRIFT ---")

    for feature, result in drift_results.items():

        print(
            f"{feature}: "
            f"PSI={result['psi']} "
            f"Status={result['status']}"
        )

    print(
        f"\nDrift Score: {drift_score}/100"
    )


    print("\n--- ANOMALY DETECTION ---")

    print(
        f"Anomalies detected: "
        f"{anomaly_count}"
    )

    print(
        f"Anomaly percentage: "
        f"{anomaly_percentage:.2f}%"
    )

    print(
        f"Anomaly Score: "
        f"{anomaly_score}/100"
    )


    print("\n--- MODEL PERFORMANCE ---")

    print(
        f"Accuracy : "
        f"{performance_metrics['accuracy']:.4f}"
    )

    print(
        f"Precision: "
        f"{performance_metrics['precision']:.4f}"
    )

    print(
        f"Recall   : "
        f"{performance_metrics['recall']:.4f}"
    )

    print(
        f"F1 Score : "
        f"{performance_metrics['f1']:.4f}"
    )

    print(
        f"Performance degradation: "
        f"{degradation * 100:.2f}%"
    )

    print(
        f"Performance Score: "
        f"{performance_score}/100"
    )


    # ==================================================
    # FINAL REPORT
    # ==================================================

    print("\n")
    print("=" * 60)
    print("             FINAL RELIABILITY")
    print("=" * 60)

    print(
        f"\nData Quality : "
        f"{data_quality_score}/100"
    )

    print(
        f"Data Drift   : "
        f"{drift_score}/100"
    )

    print(
        f"Anomalies    : "
        f"{anomaly_score}/100"
    )

    print(
        f"Performance  : "
        f"{performance_score}/100"
    )

    print(
        f"\nRELIABILITY SCORE: "
        f"{reliability_score}/100"
    )

    print(
        f"STATUS: {status}"
    )

    print("\n")


    # ==================================================
    # RETURN RESULT TO FASTAPI
    # ==================================================

    return {
        "data_quality": data_quality_score,
        "data_drift": drift_score,
        "anomalies": anomaly_score,
        "performance": performance_score,
        "reliability_score": reliability_score,
        "status": status
    }


# ==================================================
# RUN DIRECTLY
# ==================================================

if __name__ == "__main__":

    run_reliability_engine()