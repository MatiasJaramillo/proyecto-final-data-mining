import joblib
import pandas as pd


def load_model(model_path="models/final_model.pkl"):
    return joblib.load(model_path)


def predict(input_data, model_path="models/final_model.pkl"):
    model = load_model(model_path)

    if isinstance(input_data, dict):
        input_data = pd.DataFrame([input_data])

    predictions = model.predict(input_data)

    return predictions