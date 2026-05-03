"""
Prediction utilities for the trained taxi price model.
"""

from pathlib import Path

import joblib
import pandas as pd

from src.features.build_features import preprocess_data


DEFAULT_MODEL_PATH = "models/final_model.pkl"


def load_model(model_path: str = DEFAULT_MODEL_PATH):
    """
    Load the trained sklearn pipeline.
    """
    model_file = Path(model_path)

    if not model_file.exists():
        raise FileNotFoundError(
            f"Model file not found at {model_path}. "
            "Run `python -m src.models.train_model` first."
        )

    return joblib.load(model_file)


def prepare_input(input_data) -> pd.DataFrame:
    """
    Convert user input into a clean DataFrame ready for prediction.
    """
    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    elif isinstance(input_data, list):
        df = pd.DataFrame(input_data)
    elif isinstance(input_data, pd.DataFrame):
        df = input_data.copy()
    else:
        raise TypeError(
            "input_data must be a dict, list of dicts, or pandas DataFrame."
        )

    df = preprocess_data(df)

    if "total_amount" in df.columns:
        df = df.drop(columns=["total_amount"])

    return df


def predict(input_data, model_path: str = DEFAULT_MODEL_PATH):
    """
    Predict trip price using the trained pipeline.
    """
    model = load_model(model_path)
    X = prepare_input(input_data)

    predictions = model.predict(X)

    return predictions