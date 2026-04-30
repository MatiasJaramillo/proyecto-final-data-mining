import json
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.dummy import DummyRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import (
    AdaBoostRegressor,
    GradientBoostingRegressor,
    BaggingRegressor,
    VotingRegressor,
)

from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor

from src.models.evaluate_model import regression_metrics


RANDOM_STATE = 42
TARGET = "total_amount"

LEAKAGE_COLS = [
    "fare_amount",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "congestion_surcharge",
    "airport_fee",
    "extra",
    "mta_tax",
    "total_amount",
]


def prepare_xy(df: pd.DataFrame):
    df = df.copy()

    if TARGET not in df.columns:
        raise ValueError(f"Target column '{TARGET}' was not found in dataframe.")

    y = df[TARGET]

    drop_cols = [col for col in LEAKAGE_COLS if col in df.columns]
    X = df.drop(columns=drop_cols)

    return X, y


def build_preprocessor(X: pd.DataFrame):
    numeric_features = X.select_dtypes(include=["int64", "float64", "int32", "float32"]).columns.tolist()
    categorical_features = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
    )

    return preprocessor


def get_models():
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

        "xgboost": XGBRegressor(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),

        "lightgbm": LGBMRegressor(
            n_estimators=300,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),

        "catboost": CatBoostRegressor(
            iterations=300,
            learning_rate=0.05,
            depth=6,
            loss_function="RMSE",
            verbose=False,
            random_seed=RANDOM_STATE,
        ),

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
    }


def train_and_compare(train_df: pd.DataFrame, val_df: pd.DataFrame):
    X_train, y_train = prepare_xy(train_df)
    X_val, y_val = prepare_xy(val_df)

    preprocessor = build_preprocessor(X_train)
    models = get_models()

    results = {}
    trained_pipelines = {}

    for name, model in models.items():
        print(f"\nTraining {name}...")

        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model),
            ]
        )

        pipeline.fit(X_train, y_train)

        preds = pipeline.predict(X_val)
        metrics = regression_metrics(y_val, preds)

        results[name] = metrics
        trained_pipelines[name] = pipeline

        print(f"{name} RMSE: {metrics['rmse']:.4f}")

    print("\nTraining voting_ensemble...")

    voting_model = VotingRegressor(
        estimators=[
            ("xgboost", XGBRegressor(
                n_estimators=300,
                learning_rate=0.05,
                max_depth=6,
                subsample=0.8,
                colsample_bytree=0.8,
                objective="reg:squarederror",
                random_state=RANDOM_STATE,
                n_jobs=-1,
            )),
            ("lightgbm", LGBMRegressor(
                n_estimators=300,
                learning_rate=0.05,
                num_leaves=31,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            )),
            ("catboost", CatBoostRegressor(
                iterations=300,
                learning_rate=0.05,
                depth=6,
                loss_function="RMSE",
                verbose=False,
                random_seed=RANDOM_STATE,
            )),
        ],
        n_jobs=-1,
    )

    voting_pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", voting_model),
        ]
    )

    voting_pipeline.fit(X_train, y_train)
    voting_preds = voting_pipeline.predict(X_val)
    voting_metrics = regression_metrics(y_val, voting_preds)

    results["voting_ensemble"] = voting_metrics
    trained_pipelines["voting_ensemble"] = voting_pipeline

    print(f"voting_ensemble RMSE: {voting_metrics['rmse']:.4f}")

    best_model_name = min(results, key=lambda model_name: results[model_name]["rmse"])
    best_pipeline = trained_pipelines[best_model_name]

    return best_model_name, best_pipeline, results


def evaluate_on_test(best_pipeline, test_df: pd.DataFrame):
    X_test, y_test = prepare_xy(test_df)

    test_preds = best_pipeline.predict(X_test)
    test_metrics = regression_metrics(y_test, test_preds)

    return test_metrics


def save_artifacts(best_model_name, best_pipeline, results, test_metrics=None):
    Path("models").mkdir(exist_ok=True)

    joblib.dump(best_pipeline, "models/final_model.pkl")

    output = {
        "best_model": best_model_name,
        "validation_results": results,
        "test_metrics": test_metrics,
    }

    with open("models/model_metrics.json", "w") as f:
        json.dump(output, f, indent=4)

    print("\nSaved:")
    print("- models/final_model.pkl")
    print("- models/model_metrics.json")


if __name__ == "__main__":
    train_df = pd.read_parquet("data/processed/train_sample.parquet")
    val_df = pd.read_parquet("data/processed/val_sample.parquet")

    best_model_name, best_pipeline, results = train_and_compare(train_df, val_df)

    test_path = Path("data/processed/test_sample.parquet")

    if test_path.exists():
        test_df = pd.read_parquet(test_path)
        test_metrics = evaluate_on_test(best_pipeline, test_df)
        print("\nFinal Test Metrics:")
        print(test_metrics)
    else:
        test_metrics = None
        print("\nNo test sample found. Skipping final test evaluation.")

    save_artifacts(best_model_name, best_pipeline, results, test_metrics)