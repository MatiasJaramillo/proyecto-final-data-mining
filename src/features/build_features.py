"""
Notebook-derived cleaning, leakage removal, and feature preprocessing.
"""

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
    """
    Apply the cleaning and feature engineering rules from notebooks 02 and 03.
    """
    df = df.copy()
    df.columns = df.columns.str.lower()

    # Notebook 02: target and business-rule outlier filters.
    if TARGET in df.columns:
        df = df[df[TARGET].between(1.0, 500.0, inclusive="both")]

    if "trip_distance" in df.columns:
        df = df[df["trip_distance"].gt(0.1) & df["trip_distance"].lt(100.0)]

    if "passenger_count" in df.columns:
        df = df[df["passenger_count"].between(1, 9, inclusive="both")]

    if "trip_duration_min" in df.columns:
        df = df[df["trip_duration_min"].between(1.0, 300.0, inclusive="both")]

    # Notebook 02: fill nullable surcharge columns before dropping leakage.
    fill_zero_cols = ["congestion_surcharge", "airport_fee", "ehail_fee"]
    cols_to_fill = [col for col in fill_zero_cols if col in df.columns]
    if cols_to_fill:
        df[cols_to_fill] = df[cols_to_fill].fillna(0)

    location_cols = [col for col in ["pu_location_id", "do_location_id"] if col in df.columns]
    if location_cols:
        df = df.dropna(subset=location_cols)

    # Notebook 03: temporal features from pickup timestamp.
    if "pickup_datetime" in df.columns:
        pickup_datetime = pd.to_datetime(df["pickup_datetime"], errors="coerce")
        df["pickup_hour"] = pickup_datetime.dt.hour
        df["pickup_dayofweek"] = pickup_datetime.dt.dayofweek
        df["is_weekend"] = (df["pickup_dayofweek"] >= 5).astype("int64")
        df["pickup_month"] = pickup_datetime.dt.month

    # Notebook 03: route interaction from TLC location IDs.
    if {"pu_location_id", "do_location_id"}.issubset(df.columns):
        df["route_id"] = (
            df["pu_location_id"].astype(str) + "_" + df["do_location_id"].astype(str)
        )

    # Notebooks 02/03: remove leakage and raw datetime columns, preserving target.
    cols_to_drop = [
        col for col in LEAKAGE_COLS + ["pickup_datetime"] if col in df.columns and col != TARGET
    ]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)

    return df


def get_feature_pipeline(X: pd.DataFrame) -> ColumnTransformer:
    """
    Build the notebook-derived ColumnTransformer for model features present in X.
    """
    numeric_features = [
        col for col in NUMERIC_FEATURE_CANDIDATES if col in X.columns
    ]
    categorical_features = [
        col for col in CATEGORICAL_FEATURE_CANDIDATES if col in X.columns
    ]

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
