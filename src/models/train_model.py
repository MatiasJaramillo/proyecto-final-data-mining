"""Train and export the best regression model."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import (
    AdaBoostRegressor,
    BaggingRegressor,
    GradientBoostingRegressor,
    VotingRegressor,
)
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor

from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor

from src.data.ingestion import fetch_data_in_batches
from src.features.build_features import TARGET, get_feature_pipeline, preprocess_data
from src.models.evaluate_model import regression_metrics


RANDOM_STATE = 42

TRAIN_QUERY = "SELECT * FROM ANALYTICS.REFINED.TRAIN_SET SAMPLE (5) LIMIT 300000"
VAL_QUERY = "SELECT * FROM ANALYTICS.REFINED.VAL_SET SAMPLE (10) LIMIT 100000"
TEST_QUERY = "SELECT * FROM ANALYTICS.REFINED.TEST_SET SAMPLE (10) LIMIT 100000"


def load_query_as_dataframe(query: str, batch_size: int = 50_000) -> pd.DataFrame:
    """Load query results using the project batch iterator."""
    batches = []
    for batch_df in fetch_data_in_batches(query, batch_size=batch_size):
        batches.append(batch_df)

    if not batches:
        raise ValueError("No data was returned from Snowflake.")

    return pd.concat(batches, ignore_index=True)


def prepare_xy(df: pd.DataFrame):
    """Apply preprocessing and split into X/y."""
    cleaned = preprocess_data(df)

    if TARGET not in cleaned.columns:
        raise ValueError(f"Target column '{TARGET}' was not found after preprocessing.")

    X = cleaned.drop(columns=[TARGET])
    y = cleaned[TARGET]
    return X, y


def get_models():
    """Required baseline, boosting, bagging, pasting and voting models."""
    xgb_model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="reg:squarederror",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    lgbm_model = LGBMRegressor(
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    cat_model = CatBoostRegressor(
        iterations=300,
        learning_rate=0.05,
        depth=6,
        loss_function="RMSE",
        verbose=False,
        random_seed=RANDOM_STATE,
    )

    return {
        "baseline_mean": DummyRegressor(strategy="mean"),
        "adaboost": AdaBoostRegressor(
            estimator=DecisionTreeRegressor(max_depth=4, random_state=RANDOM_STATE),
            n_estimators=100,
            learning_rate=0.05,
            random_state=RANDOM_STATE,
        ),
        "gradient_boosting": GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            random_state=RANDOM_STATE,
        ),
        "xgboost": xgb_model,
        "lightgbm": lgbm_model,
        "catboost": cat_model,
        "bagging": BaggingRegressor(
            estimator=DecisionTreeRegressor(max_depth=10, random_state=RANDOM_STATE),
            n_estimators=50,
            bootstrap=True,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "pasting": BaggingRegressor(
            estimator=DecisionTreeRegressor(max_depth=10, random_state=RANDOM_STATE),
            n_estimators=50,
            bootstrap=False,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "voting_ensemble": VotingRegressor(
            estimators=[
                ("xgboost", xgb_model),
                ("lightgbm", lgbm_model),
                ("catboost", cat_model),
            ],
            n_jobs=1,
        ),
    }


def train_and_compare(X_train, y_train, X_val, y_val):
    """Train every required model and select the best by validation RMSE."""
    models = get_models()
    results = {}
    trained_pipelines = {}

    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")

        pipeline = Pipeline(
            steps=[
                ("features", get_feature_pipeline(X_train)),
                ("model", model),
            ]
        )

        pipeline.fit(X_train, y_train)
        val_preds = pipeline.predict(X_val)
        metrics = regression_metrics(y_val, val_preds)

        results[model_name] = metrics
        trained_pipelines[model_name] = pipeline

        print(f"{model_name} validation RMSE: {metrics['rmse']:.4f}")

    best_model_name = min(results, key=lambda name: results[name]["rmse"])
    best_pipeline = trained_pipelines[best_model_name]

    print("\nBest model selected using validation set:")
    print(f"{best_model_name} | RMSE: {results[best_model_name]['rmse']:.4f}")

    return best_model_name, best_pipeline, results


def save_artifacts(best_model_name, best_pipeline, validation_results, test_metrics):
    """Save model and metrics in the API default location and legacy model folder."""
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    Path("models").mkdir(exist_ok=True)

    model_path = Path("data/processed/price_model.pkl")
    legacy_model_path = Path("models/final_model.pkl")
    metrics_path = Path("models/model_metrics.json")

    joblib.dump(best_pipeline, model_path)
    joblib.dump(best_pipeline, legacy_model_path)

    output = {
        "best_model": best_model_name,
        "validation_results": validation_results,
        "test_metrics": test_metrics,
    }

    with metrics_path.open("w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    print("\nArtifacts saved:")
    print(f"- {model_path}")
    print(f"- {legacy_model_path}")
    print(f"- {metrics_path}")


def train_model():
    """Main training workflow."""
    print("Loading train sample...")
    train_df = load_query_as_dataframe(TRAIN_QUERY)

    print("Loading validation sample...")
    val_df = load_query_as_dataframe(VAL_QUERY)

    print("Loading test sample...")
    test_df = load_query_as_dataframe(TEST_QUERY)

    print("Preparing train data...")
    X_train, y_train = prepare_xy(train_df)

    print("Preparing validation data...")
    X_val, y_val = prepare_xy(val_df)

    print("Preparing test data...")
    X_test, y_test = prepare_xy(test_df)

    best_model_name, best_pipeline, validation_results = train_and_compare(
        X_train,
        y_train,
        X_val,
        y_val,
    )

    print("\nEvaluating best model once on test set...")
    test_preds = best_pipeline.predict(X_test)
    test_metrics = regression_metrics(y_test, test_preds)

    print(f"Final test RMSE: {test_metrics['rmse']:.4f}")

    save_artifacts(
        best_model_name=best_model_name,
        best_pipeline=best_pipeline,
        validation_results=validation_results,
        test_metrics=test_metrics,
    )


if __name__ == "__main__":
    train_model()
