import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (average_precision_score, classification_report,
                             confusion_matrix, roc_auc_score)
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier
from xgboost import callback as xgb_callback


def load_dataset(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found at {csv_path}")
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError("Loaded dataset is empty; verify the source file")
    return df


def infer_feature_types(df: pd.DataFrame, target: str):
    features = df.drop(columns=[target])
    categorical_cols = features.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    numeric_cols = features.select_dtypes(include=[np.number]).columns.tolist()
    return categorical_cols, numeric_cols


def build_preprocessor(categorical_cols, numeric_cols):
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=True, dtype=np.float32)),
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_pipeline, numeric_cols),
        ("cat", categorical_pipeline, categorical_cols),
    ], remainder="drop")

    return preprocessor


def train_model(df: pd.DataFrame, target: str, random_state: int = 42):
    X = df.drop(columns=[target])
    y = df[target]

    categorical_cols, numeric_cols = infer_feature_types(df, target)
    preprocessor = build_preprocessor(categorical_cols, numeric_cols)

    # Fit preprocessor on full data
    preprocessor.fit(X)

    X_encoded = preprocessor.transform(X)

    # Build XGBoost model and train on full data (no eval_set for validation)
    model = XGBClassifier(
        objective="binary:logistic",
        use_label_encoder=False,
        eval_metric="auc",
        tree_method="hist",
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        n_estimators=500,
        reg_lambda=1.0,
        scale_pos_weight=None,
        random_state=random_state,
        n_jobs=-1,
    )

    # Train on full data without eval_set
    model.fit(X_encoded, y, verbose=True)

    # Build a pipeline object using the fitted preprocessor and model for downstream inference
    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])

    # Predict on full data (not ideal for evaluation, but for completeness)
    if hasattr(X_encoded, "toarray"):
        X_for_pred = X_encoded
    else:
        X_for_pred = X_encoded

    y_proba = model.predict_proba(X_for_pred)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    metrics = {
        "roc_auc": roc_auc_score(y, y_proba),
        "average_precision": average_precision_score(y, y_proba),
        "classification_report": classification_report(y, y_pred, output_dict=True),
        "confusion_matrix": confusion_matrix(y, y_pred).tolist(),
        "note": "Metrics computed on training data (full dataset) - not a proper holdout evaluation."
    }

    # Compute SHAP values on a sample for performance
    transformer = pipeline.named_steps["preprocessor"]
    booster = pipeline.named_steps["model"]
    feature_names = transformer.get_feature_names_out()

    # Sample from full data for SHAP
    encoded_sample = transformer.transform(X)[:1000]

    if hasattr(encoded_sample, "toarray"):
        X_dense = encoded_sample.toarray().astype(np.float32, copy=False)
    else:
        X_dense = np.asarray(encoded_sample, dtype=np.float32)

    sample_size = X_dense.shape[0]
    background = shap.utils.sample(X_dense, min(200, sample_size))
    explainer = shap.TreeExplainer(booster, data=background, feature_names=feature_names)
    shap_values = explainer.shap_values(X_dense)

    shap_summary = {
        "feature_names": feature_names.tolist(),
        "mean_abs_shap": np.abs(shap_values).mean(axis=0).tolist(),
    }

    return pipeline, metrics, shap_summary


def save_artifacts(pipeline, metrics, shap_summary, model_dir: Path, reports_dir: Path):
    model_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "xgb_churn_pipeline.pkl"
    joblib.dump(pipeline, model_path)

    metrics_path = reports_dir / "metrics.json"
    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    shap_path = reports_dir / "shap_summary.json"
    with shap_path.open("w", encoding="utf-8") as f:
        json.dump(shap_summary, f, indent=2)

    # If evals_result was produced by XGBoost, save it as well
    try:
        # metrics may contain an 'evals_result' key
        if "evals_result" in metrics:
            evals_path = reports_dir / "evals_result.json"
            with evals_path.open("w", encoding="utf-8") as ef:
                json.dump(metrics["evals_result"], ef, indent=2)
    except Exception:
        pass

    return {
        "model": str(model_path),
        "metrics": str(metrics_path),
        "shap_summary": str(shap_path),
    }


def parse_args():
    parser = argparse.ArgumentParser(description="Train XGBoost churn model with SHAP explainability")
    parser.add_argument("--data-path", type=Path, required=True, help="Path to training CSV")
    parser.add_argument("--target", type=str, default="churn", help="Name of target column")
    parser.add_argument("--model-dir", type=Path, default=Path("models"), help="Directory to store trained model")
    parser.add_argument("--reports-dir", type=Path, default=Path("reports/metrics"), help="Directory to store metrics and SHAP summary")
    parser.add_argument("--random-state", type=int, default=42)

    return parser.parse_args()


def main():
    args = parse_args()
    df = load_dataset(args.data_path)
    if args.target not in df.columns:
        raise ValueError(f"Target column '{args.target}' not found; available columns: {df.columns.tolist()}")

    pipeline, metrics, shap_summary = train_model(df, args.target, args.random_state)
    artifact_paths = save_artifacts(pipeline, metrics, shap_summary, args.model_dir, args.reports_dir)

    print("Training complete. Artifacts saved:")
    for name, path in artifact_paths.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()
