"""
Módulo para las transformaciones lógicas y feature engineering.
Ideal para colocar tus scikit-learn Pipelines personalizados y limpieza robusta.
"""
import pandas as pd
from sklearn.pipeline import Pipeline

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica limpieza básica y eliminación de columnas que generen leakage."""
    # TODO: Implementar lógica de filtrado inicial (basada en el notebook 02)
    pass

def get_feature_pipeline() -> Pipeline:
    """Devuelve el pipeline de transformaciones preparatorio para el modelo."""
    # TODO: Implementar ColumnTransformer (escalado, encoding, etc.) (basado en el notebook 03)
    pass
