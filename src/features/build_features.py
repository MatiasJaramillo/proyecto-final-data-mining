"""Notebook-derived cleaning, leakage removal, and feature preprocessing."""
from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


TARGET = "total_amount"

LEAKAGE_COLS = [
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "congestion_surcharge",
    "airport_fee",
    "ehail_fee",
    "tip_pct",
    "dropoff_datetime",
    "trip_duration_min",
    "avg_speed_mph",
    "payment_type",
    "trip_type",
    "store_and_fwd_flag",
    "run_id",
    "ingested_at_utc",
]

NUMERIC_FEATURE_CANDIDATES = [
    "passenger_count",
    "trip_distance",
    "pickup_hour",
    "pickup_dayofweek",
    "pickup_month",
]

CATEGORICAL_FEATURE_CANDIDATES = [
    "vendor_id",
    "rate_code_id",
    "pu_location_id",
    "do_location_id",
    "service_type",
    "is_weekend",
    "route_id",
]


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply cleaning and feature engineering rules from notebooks 02 and 03."""
    data = df.copy()
    data.columns = data.columns.str.lower()

    if "taxi_type" in data.columns and "service_type" not in data.columns:
        data["service_type"] = data["taxi_type"]
    if "source_year" in data.columns:
        data["source_year"] = pd.to_numeric(data["source_year"], errors="coerce")

    # Training-time filters only run when target exists, so API inference keeps one row.
    if TARGET in data.columns:
        data = data[data[TARGET].between(1.0, 500.0, inclusive="both")]
        if "trip_distance" in data.columns:
            data = data[data["trip_distance"].gt(0.1) & data["trip_distance"].lt(100.0)]
        if "passenger_count" in data.columns:
            data = data[data["passenger_count"].between(1, 9, inclusive="both")]
        if "trip_duration_min" in data.columns:
            data = data[data["trip_duration_min"].between(1.0, 300.0, inclusive="both")]

    if "trip_distance" in data.columns:
        data["trip_distance"] = pd.to_numeric(data["trip_distance"], errors="coerce").clip(0.01, 150)
    if "passenger_count" in data.columns:
        data["passenger_count"] = pd.to_numeric(data["passenger_count"], errors="coerce").clip(0, 9)

    fill_zero_cols = ["congestion_surcharge", "airport_fee", "ehail_fee"]
    cols_to_fill = [col for col in fill_zero_cols if col in data.columns]
    if cols_to_fill:
        data[cols_to_fill] = data[cols_to_fill].fillna(0)

    location_cols = [col for col in ["pu_location_id", "do_location_id"] if col in data.columns]
    if TARGET in data.columns and location_cols:
        data = data.dropna(subset=location_cols)

    if "pickup_datetime" in data.columns:
        pickup_datetime = pd.to_datetime(data["pickup_datetime"], errors="coerce")
        data["pickup_hour"] = pickup_datetime.dt.hour
        data["pickup_dayofweek"] = pickup_datetime.dt.dayofweek
        data["is_weekend"] = (data["pickup_dayofweek"] >= 5).astype("Int64")
        data["pickup_month"] = pickup_datetime.dt.month

    if {"pu_location_id", "do_location_id"}.issubset(data.columns):
        data["route_id"] = (
            data["pu_location_id"].astype("Int64").astype(str)
            + "_"
            + data["do_location_id"].astype("Int64").astype(str)
        )

    cols_to_drop = [
        col for col in LEAKAGE_COLS + ["pickup_datetime", "taxi_type"] if col in data.columns
    ]
    if cols_to_drop:
        data = data.drop(columns=cols_to_drop)

    return data


def get_feature_pipeline(X: pd.DataFrame | None = None) -> ColumnTransformer:
    """Build the notebook-derived ColumnTransformer for model features present in X."""
    if X is None:
        numeric_features = NUMERIC_FEATURE_CANDIDATES
        categorical_features = CATEGORICAL_FEATURE_CANDIDATES
    else:
        numeric_features = [col for col in NUMERIC_FEATURE_CANDIDATES if col in X.columns]
        categorical_features = [col for col in CATEGORICAL_FEATURE_CANDIDATES if col in X.columns]

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

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ],
        remainder="drop",
    )
