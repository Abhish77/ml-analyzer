import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

# --------------------------------------------------
# 1. Load cleaned dataset
# --------------------------------------------------

DATA_FILE = "data/processed/clean_churn_data.csv"
MODEL_FILE = "models/churn_model.pkl"

df = pd.read_csv(DATA_FILE)

print("Dataset shape:", df.shape)

# --------------------------------------------------
# 2. Separate features and target
# --------------------------------------------------

X = df.drop(columns=["Churn"])
y = df["Churn"]

# --------------------------------------------------
# 3. Identify column types
# --------------------------------------------------

categorical_columns = X.select_dtypes(
    include=["object"]
).columns

numerical_columns = X.select_dtypes(
    exclude=["object"]
).columns

print("\nCategorical columns:")
print(list(categorical_columns))

print("\nNumerical columns:")
print(list(numerical_columns))

# --------------------------------------------------
# 4. Preprocessing
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_columns
        ),
        (
            "numerical",
            "passthrough",
            numerical_columns
        )
    ]
)

# --------------------------------------------------
# 5. Create ML model
# --------------------------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)

# --------------------------------------------------
# 6. Create complete ML pipeline
# --------------------------------------------------

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)

# --------------------------------------------------
# 7. Split dataset
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))

# --------------------------------------------------
# 8. Train model
# --------------------------------------------------

print("\nTraining model...")

pipeline.fit(X_train, y_train)

# --------------------------------------------------
# 9. Save trained model
# --------------------------------------------------

joblib.dump(pipeline, MODEL_FILE)

print("\nModel saved to:", MODEL_FILE)

# --------------------------------------------------
# 10. Make predictions
# --------------------------------------------------

y_pred = pipeline.predict(X_test)

# --------------------------------------------------
# 11. Calculate performance metrics
# --------------------------------------------------

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

# --------------------------------------------------
# 12. Display baseline performance
# --------------------------------------------------

print("\n--- BASELINE MODEL PERFORMANCE ---")

print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1 Score : {f1:.4f}")

# --------------------------------------------------
# 13. Detailed classification report
# --------------------------------------------------

print("\n--- CLASSIFICATION REPORT ---")

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)