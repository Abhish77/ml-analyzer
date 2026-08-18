def calculate_reliability_score(
    data_quality_score,
    drift_score,
    anomaly_score,
    performance_score
):
    """
    Calculate an overall ML reliability score.
    """

    score = (
        data_quality_score * 0.25
        + drift_score * 0.25
        + anomaly_score * 0.20
        + performance_score * 0.30
    )

    score = round(score, 2)

    if score >= 80:
        status = "Healthy"

    elif score >= 60:
        status = "Warning"

    else:
        status = "Critical"

    return score, status


if __name__ == "__main__":

    # Current healthy-state example
    data_quality = 100
    drift = 100
    anomalies = 95
    performance = 100

    score, status = calculate_reliability_score(
        data_quality,
        drift,
        anomalies,
        performance
    )

    print("\n--- ML RELIABILITY SCORE ---")

    print(
        f"Data Quality : {data_quality}/100"
    )

    print(
        f"Data Drift   : {drift}/100"
    )

    print(
        f"Anomalies    : {anomalies}/100"
    )

    print(
        f"Performance  : {performance}/100"
    )

    print(
        f"\nReliability Score: {score}/100"
    )

    print(
        f"Status: {status}"
    )