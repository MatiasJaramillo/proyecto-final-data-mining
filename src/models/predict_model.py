"""Prediction utilities for the trained taxi price model."""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from src.features.build_features import TARGET, preprocess_data


DEFAULT_MODEL_PATH = Path("data/processed/price_model.pkl")
LEGACY_MODEL_PATH = Path("models/final_model.pkl")


def resolve_model_path(model_path: str | Path | None = None) -> Path:
    """Return the requested model path or the first known local artifact."""
    if model_path is not None:
        return Path(model_path)
    if DEFAULT_MODEL_PATH.exists():
        return DEFAULT_MODEL_PATH
    return LEGACY_MODEL_PATH


def load_model(model_path: str | Path | None = None):
    """Load the trained sklearn pipeline."""
    path = resolve_model_path(model_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Model file not found at {path}. Run `python -m src.models.train_model` first."
        )
    return joblib.load(path)


def prepare_input(input_data) -> pd.DataFrame:
    """Convert user input into a clean DataFrame ready for prediction."""
    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    elif isinstance(input_data, list):
        df = pd.DataFrame(input_data)
    elif isinstance(input_data, pd.DataFrame):
        df = input_data.copy()
    else:
        raise TypeError("input_data must be a dict, list of dicts, or pandas DataFrame.")

    df = preprocess_data(df)
    if TARGET in df.columns:
        df = df.drop(columns=[TARGET])
    return df


def predict(model, input_data) -> list[float]:
    """Predict trip price with an already loaded model."""
    X = prepare_input(input_data)
    predictions = model.predict(X)
    return [float(value) for value in predictions]


def predict_from_path(input_data, model_path: str | Path | None = None) -> list[float]:
    """Load a model from disk and predict trip prices."""
    model = load_model(model_path)
    return predict(model, input_data)
