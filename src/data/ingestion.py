"""
Módulo para la conexión a Snowflake y extracción de datos iterativa (Big Data).
"""
import pandas as pd
import os
import snowflake.connector
from typing import Iterator
from src.utils.config import get_snowflake_credentials

def get_snowflake_connection():
    """Establece y retorna un objeto de conexión de Snowflake."""
    creds = get_snowflake_credentials()
    # TODO: Implementar la conexión de la librería snowflake.connector
    return None

def fetch_data_in_batches(query: str, batch_size: int = 100000) -> Iterator[pd.DataFrame]:
    """
    Extrae datos de Snowflake mediante cursores/lotes en lugar de cargar todo el DataFrame.
    Crucial para datasets de 20GB.
    
    Devuelve un iterador (yield) de pandas DataFrames para entrenamiento Out-of-Core.
    """
    conn = get_snowflake_connection()
    if conn is None:
        raise ConnectionError("No se pudo conectar a Snowflake.")
        
    # TODO: Ejecutar cursor.execute(query) 
    # TODO: Usar un bucle while True para llamar fetchmany(batch_size) o fetch_pandas_batches()
    # TODO: yield dataframe_batch
    pass

def fetch_sample(query: str, sample_prob: float = 1.0) -> pd.DataFrame:
    """Extrae una muestra única para experimentación en Jupyter (EDA)."""
    # TODO: Inyectar 'SAMPLE (sample_prob)' en el query y hacer fetchall() tradicional
    pass
