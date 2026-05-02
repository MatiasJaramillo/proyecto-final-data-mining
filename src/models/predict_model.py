"""
Módulo para realizar predicciones aislando la carga del modelo para su uso final.
"""
import joblib
import pandas as pd

def load_model(model_path: str):
    """Carga el modelo serializado (ej. el archivo .pkl)."""
    # TODO: Implementar carga
    pass

def predict(model, input_data: pd.DataFrame) -> list:
    """Recibe datos crudos, aplica pipeline y genera estimaciones de total_amount."""
    # TODO: Llamar a model.predict(input_data)
    pass
