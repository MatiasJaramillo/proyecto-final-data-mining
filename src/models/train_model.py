"""
Script principal para entrenar y exportar el modelo ganador usando Out-of-Core learning.
"""
import pandas as pd
import joblib
# Ejemplo: import xgboost as xgb o import lightgbm as lgb
from src.data.ingestion import fetch_data_in_batches
from src.features.build_features import get_feature_pipeline

def train_out_of_core():
    """
    Entrena el modelo procesando datos en partes mediante iteradores.
    Herramientas como XGBoost, LightGBM y CatBoost lo soportan nativamente.
    """
    print("Iniciando carga iterativa para prevenir MemoryError...")
    
    # 1. Definir la query a la vista particionada en Snowflake
    query_train = "SELECT * FROM analytics.train_set"
    
    # 2. Obtener el pipeline base (StandardScaler, etc.)
    pipeline = get_feature_pipeline()
    
    # TODO: Instanciar estimador enfocado en incrementales 
    # Ej. LightGBM Dataset o XGBoost iterativo
    
    # 3. Iterar
    # for batch_df in fetch_data_in_batches(query_train, batch_size=500000):
    #     X_chunk = batch_df.drop('total_amount', axis=1)
    #     y_chunk = batch_df['total_amount']
    #     # Transformar chunk
    #     # Actualizar modelo (partial_fit o equivalente)
    
    # 4. Exportar el modelo
    # joblib.dump(modelo_final, 'models/price_model_ooc.pkl')
    pass

if __name__ == "__main__":
    train_out_of_core()
