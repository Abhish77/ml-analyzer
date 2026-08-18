import ast
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

IGNORED_DIRS = {
    ".git",
    ".github",
    "__pycache__",
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "dist",
    "build",
    ".idea",
    ".vscode",
}

MAX_FILE_SIZE = 2 * 1024 * 1024

ML_LIBRARIES = {
    "scikit-learn": [
        "sklearn",
        "scikit-learn",
    ],
    "Pandas": [
        "pandas",
    ],
    "NumPy": [
        "numpy",
    ],
    "TensorFlow": [
        "tensorflow",
        "keras",
    ],
    "PyTorch": [
        "torch",
        "torchvision",
    ],
    "XGBoost": [
        "xgboost",
    ],
    "LightGBM": [
        "lightgbm",
    ],
    "CatBoost": [
        "catboost",
    ],
    "SciPy": [
        "scipy",
    ],
}

ML_KEYWORDS = [
    "machine learning",
    "machine-learning",
    "deep learning",
    "model training",
    "model.fit",
    "train_test_split",
    "classification",
    "regression",
    "random forest",
    "randomforest",
    "decision tree",
    "logistic regression",
    "linear regression",
    "gradient boosting",
    "neural network",
    "neural_network",
    "cnn",
    "rnn",
    "lstm",
    "transformer",
    "predict",
    "prediction",
    "predict_proba",
    "cross_val_score",
    "accuracy_score",
    "precision_score",
    "recall_score",
    "f1_score",
    "confusion_matrix",
    "roc_auc",
    "train_test_split",
    "fit(",
    "predict(",
]

DATA_KEYWORDS = [
    "dataset",
    "data.csv",
    "train.csv",
    "test.csv",
    "validation",
    "preprocessing",
    "feature",
    "features",
    "target",
    "label",
]

DRIFT_KEYWORDS = [
    "drift",
    "data drift",
    "distribution",
    "distribution shift",
    "psi",
    "population stability",
    "evidently",
    "kolmogorov",
    "ks_2samp",
]

ANOMALY_KEYWORDS = [
    "anomaly",
    "outlier",
    "isolationforest",
    "isolation forest",
    "localoutlierfactor",
    "local outlier factor",
    "oneclasssvm",
    "one class svm",
]

PERFORMANCE_KEYWORDS = [
    "accuracy",
    "precision",
    "recall",
    "f1",
    "f1_score",
    "roc_auc",
    "auc",
    "mae",
    "mse",
    "rmse",
    "r2_score",
    "classification_report",
    "confusion_matrix",
    "cross_val",
    "cross validation",
]

LEAKAGE_KEYWORDS = [
    "data leakage",
    "leakage",
    "target leakage",
]

REPRODUCIBILITY_KEYWORDS = [
    "random_state",
    "random seed",
    "seed(",
    "requirements.txt",
    "environment.yml",
    "pyproject.toml",
    "poetry.lock",
    "pipfile",
]


# ============================================================
# BASIC HELPERS
# ============================================================

def clean_repository_url(url: str) -> str:
    url = url.strip()

    if url.endswith("/"):
        url = url[:-1]

    if url.endswith(".git"):
        url = url[:-4]

    # Remove accidental query strings/fragments.
    url = url.split("?")[0]
    url = url.split("#")[0]

    return url


def is_valid_github_url(url: str) -> bool:
    pattern = r"^https?://(www\.)?github\.com/[^/]+/[^/]+/?$"
    return bool(re.match(pattern, url.strip()))


def clone_repository(repository_url: str, destination: str):
    """
    Clone a public GitHub repository without using GitHub's REST API.
    """

    repository_url = clean_repository_url(repository_url)

    if not is_valid_github_url(repository_url):
        raise ValueError(
            "Please provide a valid public GitHub repository URL."
        )

    command = [
        "git",
        "clone",
        "--depth",
        "1",
        repository_url,
        destination,
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Git is not installed on the system. "
            "Please install Git and try again."
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "Repository cloning timed out. "
            "The repository may be too large or unavailable."
        )

    if result.returncode != 0:
        error = result.stderr.strip()

        if "not found" in error.lower():
            raise RuntimeError(
                "Repository not found. Make sure the GitHub URL is correct "
                "and the repository is public."
            )

        if "authentication" in error.lower():
            raise RuntimeError(
                "This repository appears to require authentication. "
                "Only public repositories are supported."
            )

        raise RuntimeError(
            f"Unable to clone repository: {error}"
        )


def get_files(root: Path):
    files = []

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        relative_parts = path.relative_to(root).parts

        if any(part in IGNORED_DIRS for part in relative_parts):
            continue

        try:
            if path.stat().st_size > MAX_FILE_SIZE:
                continue
        except OSError:
            continue

        files.append(path)

    return files


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
    except Exception:
        return ""


def repository_text(files):
    chunks = []

    for file in files:

        try:
            if file.stat().st_size > MAX_FILE_SIZE:
                continue
        except OSError:
            continue

        text = read_text_file(file)

        if text:
            chunks.append(
                f"\n--- {file.name} ---\n{text[:500000]}"
            )

    return "\n".join(chunks)


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_languages(files):

    extension_map = {
        ".py": "Python",
        ".ipynb": "Jupyter Notebook",
        ".js": "JavaScript",
        ".jsx": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript",
        ".java": "Java",
        ".cpp": "C++",
        ".cc": "C++",
        ".c": "C",
        ".cs": "C#",
        ".go": "Go",
        ".rs": "Rust",
        ".php": "PHP",
        ".rb": "Ruby",
        ".r": "R",
        ".sql": "SQL",
    }

    languages = set()

    for file in files:

        extension = file.suffix.lower()

        if extension in extension_map:
            languages.add(extension_map[extension])

    return sorted(languages)


# ============================================================
# ML LIBRARY DETECTION
# ============================================================

def detect_ml_libraries(files):

    found = set()

    for file in files:

        if file.suffix.lower() not in {
            ".py",
            ".ipynb",
            ".txt",
            ".md",
            ".toml",
            ".yaml",
            ".yml",
        }:
            continue

        text = read_text_file(file).lower()

        for library, patterns in ML_LIBRARIES.items():

            for pattern in patterns:

                if pattern.lower() in text:
                    found.add(library)
                    break

    return sorted(found)


# ============================================================
# ML CODE DETECTION
# ============================================================

def detect_ml_code(files):

    indicators = []

    for file in files:

        if file.suffix.lower() != ".py":
            continue

        text = read_text_file(file)

        lower_text = text.lower()

        matches = []

        for keyword in ML_KEYWORDS:

            if keyword.lower() in lower_text:
                matches.append(keyword)

        if not matches:
            continue

        # Prefer actual model.fit() detection.
        if "model.fit(" in lower_text:
            indicator = "model.fit()"
        elif "train_test_split" in lower_text:
            indicator = "train_test_split()"
        elif "predict(" in lower_text:
            indicator = "predict()"
        else:
            indicator = matches[0]

        indicators.append(
            {
                "file": str(file.name),
                "indicator": indicator,
                "detection_reasons": [
                    "ML-related code detected"
                ],
            }
        )

    return indicators


# ============================================================
# README / DESCRIPTION
# ============================================================

def find_readme(files):

    for file in files:

        if file.name.lower() in {
            "readme",
            "readme.md",
            "readme.txt",
            "readme.rst",
        }:
            return read_text_file(file)

    return ""


# ============================================================
# PROJECT CLASSIFICATION
# ============================================================

def classify_project(
    files,
    languages,
    ml_libraries,
    ml_code,
    readme,
):

    score = 0
    reasons = []

    combined_text = readme.lower()

    for file in files:

        if file.suffix.lower() not in {
            ".py",
            ".ipynb",
            ".md",
            ".txt",
            ".toml",
            ".yaml",
            ".yml",
        }:
            continue

        combined_text += "\n" + read_text_file(file).lower()[:100000]

    # ML libraries
    if ml_libraries:
        score += 35
        reasons.append("ML libraries detected")

    # ML code
    if ml_code:
        score += 40
        reasons.append("ML-related code detected")

    # ML keywords
    keyword_hits = 0

    for keyword in ML_KEYWORDS:

        if keyword.lower() in combined_text:
            keyword_hits += 1

    if keyword_hits >= 3:
        score += 20
        reasons.append("Multiple ML indicators detected")
    elif keyword_hits >= 1:
        score += 10
        reasons.append("ML description or code indicators detected")

    # Python
    if "Python" in languages and (
        ml_libraries or ml_code
    ):
        score += 5

    score = min(score, 98)

    is_ml = score >= 50

    if is_ml:

        description = (
            "This repository appears to be a machine-learning project "
            "with identifiable ML libraries, model-related code or "
            "machine-learning components."
        )

        project_type = "Machine Learning Project"

    else:

        description = (
            "No clear machine-learning model or ML pipeline was detected "
            "in this repository."
        )

        project_type = "Not an ML Project"

    return {
        "type": project_type,
        "is_ml_project": is_ml,
        "confidence": score,
        "description": description,
        "reasons": reasons,
    }


# ============================================================
# FILE DETECTION
# ============================================================

def detect_ml_files(files):

    ml_files = []

    patterns = [
        "model",
        "train",
        "training",
        "predict",
        "prediction",
        "dataset",
        "preprocess",
        "pipeline",
        "classifier",
        "regression",
        "inference",
    ]

    for file in files:

        name = file.name.lower()

        if any(pattern in name for pattern in patterns):

            ml_files.append(
                str(file.relative_to(file.parents[len(file.parts) - 1]))
                if False
                else file.name
            )

    return sorted(set(ml_files))[:50]


# ============================================================
# GENERIC TEXT INDICATOR
# ============================================================

def contains_keywords(text, keywords):

    lower = text.lower()

    return [
        keyword
        for keyword in keywords
        if keyword.lower() in lower
    ]


# ============================================================
# DATA QUALITY
# ============================================================

def analyze_data_quality(files, text):

    score = 60
    findings = []

    has_dataset = any(
        file.suffix.lower() in {".csv", ".parquet", ".xlsx", ".json"}
        for file in files
    )

    has_pandas = "pandas" in text.lower()

    has_missing_value_handling = any(
        keyword in text.lower()
        for keyword in [
            "fillna",
            "dropna",
            "isnull",
            "notnull",
            "missing",
            "imputer",
            "simpleimputer",
        ]
    )

    if has_dataset:
        score += 10
        findings.append("Dataset files detected.")

    if has_pandas:
        score += 10
        findings.append("Pandas-based data processing detected.")

    if has_missing_value_handling:
        score += 15
        findings.append("Missing-value handling detected.")
    else:
        findings.append(
            "No clear missing-value handling strategy was detected."
        )

    score = min(score, 100)

    if score >= 85:
        status = "Excellent"
    elif score >= 70:
        status = "Good"
    else:
        status = "Needs Attention"

    return {
        "score": score,
        "status": status,
        "findings": findings,
    }


# ============================================================
# DATA DRIFT
# ============================================================

def analyze_data_drift(text):

    matches = contains_keywords(
        text,
        DRIFT_KEYWORDS,
    )

    if matches:

        return {
            "score": 90,
            "status": "Monitored",
            "detected": True,
            "findings": [
                "Data-distribution monitoring indicators were detected.",
                f"Indicators: {', '.join(matches[:6])}",
            ],
        }

    return {
        "score": 40,
        "status": "Needs Attention",
        "detected": False,
        "findings": [
            "No clear data-drift monitoring implementation was detected.",
            "Consider monitoring changes in production data distributions.",
        ],
    }


# ============================================================
# ANOMALIES
# ============================================================

def analyze_anomalies(text):

    matches = contains_keywords(
        text,
        ANOMALY_KEYWORDS,
    )

    if matches:

        return {
            "score": 90,
            "status": "Detected",
            "detected": True,
            "findings": [
                "Anomaly or outlier detection indicators were detected."
            ],
        }

    return {
        "score": 60,
        "status": "Not Detected",
        "detected": False,
        "findings": [
            "No explicit anomaly-detection mechanism was detected."
        ],
    }


# ============================================================
# MODEL PERFORMANCE
# ============================================================

def analyze_performance(text):

    matches = contains_keywords(
        text,
        PERFORMANCE_KEYWORDS,
    )

    if len(matches) >= 4:

        score = 95
        status = "Excellent"

    elif len(matches) >= 2:

        score = 80
        status = "Good"

    elif len(matches) >= 1:

        score = 65
        status = "Limited"

    else:

        score = 40
        status = "Needs Attention"

    return {
        "score": score,
        "status": status,
        "metrics_detected": matches[:15],
        "findings": (
            ["Model evaluation metrics were detected."]
            if matches
            else
            [
                "No clear model evaluation metrics were detected."
            ]
        ),
    }


# ============================================================
# DATA LEAKAGE
# ============================================================

def analyze_leakage(text):

    matches = contains_keywords(
        text,
        LEAKAGE_KEYWORDS,
    )

    if matches:

        return {
            "score": 60,
            "status": "Review Required",
            "detected": True,
            "findings": [
                "The repository contains references to data leakage."
            ],
        }

    return {
        "score": 85,
        "status": "No Obvious Leakage Indicator",
        "detected": False,
        "findings": [
            "No explicit data-leakage warning was detected in the "
            "available repository evidence."
        ],
    }


# ============================================================
# REPRODUCIBILITY
# ============================================================

def analyze_reproducibility(files, text):

    matches = contains_keywords(
        text,
        REPRODUCIBILITY_KEYWORDS,
    )

    score = 40
    findings = []

    filenames = {
        file.name.lower()
        for file in files
    }

    if "requirements.txt" in filenames:
        score += 20
        findings.append("requirements.txt detected.")

    if "environment.yml" in filenames:
        score += 20
        findings.append("environment.yml detected.")

    if "pyproject.toml" in filenames:
        score += 15
        findings.append("pyproject.toml detected.")

    if "random_state" in text.lower():
        score += 15
        findings.append("random_state detected.")

    if not findings:
        findings.append(
            "Limited reproducibility configuration was detected."
        )

    score = min(score, 100)

    if score >= 80:
        status = "Excellent"
    elif score >= 60:
        status = "Good"
    else:
        status = "Needs Attention"

    return {
        "score": score,
        "status": status,
        "findings": findings,
        "indicators": matches[:15],
    }


# ============================================================
# OVERALL RELIABILITY
# ============================================================

def calculate_reliability(
    data_quality,
    data_drift,
    anomalies,
    performance,
    leakage,
    reproducibility,
):

    scores = [
        data_quality["score"],
        data_drift["score"],
        anomalies["score"],
        performance["score"],
        leakage["score"],
        reproducibility["score"],
    ]

    overall = round(sum(scores) / len(scores))

    if overall >= 85:
        status = "Excellent"
    elif overall >= 70:
        status = "Healthy"
    elif overall >= 50:
        status = "Needs Attention"
    else:
        status = "At Risk"

    return overall, status


# ============================================================
# RECOMMENDATIONS
# ============================================================

def generate_recommendations(
    data_quality,
    data_drift,
    anomalies,
    performance,
    leakage,
    reproducibility,
):

    recommendations = []

    if data_quality["score"] < 80:
        recommendations.append(
            "Add stronger data-quality checks and explicit missing-value handling."
        )

    if data_drift["score"] < 70:
        recommendations.append(
            "Add data-drift monitoring to detect changes in production data."
        )

    if anomalies["score"] < 70:
        recommendations.append(
            "Consider adding anomaly or outlier detection."
        )

    if performance["score"] < 70:
        recommendations.append(
            "Add clear model evaluation metrics and validation."
        )

    if leakage["detected"]:
        recommendations.append(
            "Review the pipeline carefully for possible target or data leakage."
        )

    if reproducibility["score"] < 70:
        recommendations.append(
            "Add dependency/version management and reproducible random seeds."
        )

    if not recommendations:
        recommendations.append(
            "The repository shows strong reliability indicators. "
            "Continue monitoring the model after deployment."
        )

    return recommendations


# ============================================================
# MAIN ANALYZER
# ============================================================

def analyze_repository(repository_url: str):

    repository_url = clean_repository_url(repository_url)

    temp_directory = tempfile.mkdtemp(
        prefix="ml_analyzer_"
    )

    try:

        repository_directory = os.path.join(
            temp_directory,
            "repository",
        )

        # ----------------------------------------------------
        # Clone repository
        # ----------------------------------------------------

        clone_repository(
            repository_url,
            repository_directory,
        )

        root = Path(repository_directory)

        # ----------------------------------------------------
        # Collect files
        # ----------------------------------------------------

        files = get_files(root)

        if not files:
            raise RuntimeError(
                "The repository contains no readable files."
            )

        # ----------------------------------------------------
        # Basic repository information
        # ----------------------------------------------------

        languages = detect_languages(files)

        ml_libraries = detect_ml_libraries(files)

        ml_code = detect_ml_code(files)

        readme = find_readme(files)

        all_text = repository_text(files)

        # ----------------------------------------------------
        # Classification
        # ----------------------------------------------------

        project = classify_project(
            files=files,
            languages=languages,
            ml_libraries=ml_libraries,
            ml_code=ml_code,
            readme=readme,
        )

        # ----------------------------------------------------
        # If not ML
        # ----------------------------------------------------

        if not project["is_ml_project"]:

            return {
                "success": True,
                "repository": repository_url,

                "project": project,

                "detected": {
                    "languages": languages,
                    "ml_libraries": ml_libraries,
                    "ml_files": [],
                    "ml_code_indicators": ml_code,
                },

                "analyzers": {},

                "reliability": {
                    "score": 0,
                    "status": "Not Applicable",
                },

                "recommendations": [
                    "This website is designed for machine-learning "
                    "projects. Please provide a repository containing "
                    "an ML model or ML pipeline."
                ],
            }

        # ----------------------------------------------------
        # Reliability analyzers
        # ----------------------------------------------------

        data_quality = analyze_data_quality(
            files,
            all_text,
        )

        data_drift = analyze_data_drift(
            all_text,
        )

        anomalies = analyze_anomalies(
            all_text,
        )

        performance = analyze_performance(
            all_text,
        )

        leakage = analyze_leakage(
            all_text,
        )

        reproducibility = analyze_reproducibility(
            files,
            all_text,
        )

        # ----------------------------------------------------
        # Overall score
        # ----------------------------------------------------

        reliability_score, reliability_status = calculate_reliability(
            data_quality,
            data_drift,
            anomalies,
            performance,
            leakage,
            reproducibility,
        )

        # ----------------------------------------------------
        # Recommendations
        # ----------------------------------------------------

        recommendations = generate_recommendations(
            data_quality,
            data_drift,
            anomalies,
            performance,
            leakage,
            reproducibility,
        )

        # ----------------------------------------------------
        # Final result
        # ----------------------------------------------------

        return {
            "success": True,

            "repository": repository_url,

            "project": project,

            "detected": {
                "languages": languages,
                "ml_libraries": ml_libraries,
                "ml_files": detect_ml_files(files),
                "ml_code_indicators": ml_code,
            },

            "analyzers": {
                "data_quality": data_quality,
                "data_drift": data_drift,
                "anomalies": anomalies,
                "performance": performance,
                "data_leakage": leakage,
                "reproducibility": reproducibility,
            },

            "reliability": {
                "score": reliability_score,
                "status": reliability_status,
            },

            "recommendations": recommendations,
        }

    finally:

        # ----------------------------------------------------
        # Always delete temporary clone
        # ----------------------------------------------------

        shutil.rmtree(
            temp_directory,
            ignore_errors=True,
        )