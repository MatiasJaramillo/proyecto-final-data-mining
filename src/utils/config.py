"""
Módulo utilitario para la recolección de variables de entorno y configuración central.
"""
import os
from dotenv import load_dotenv

# Carga variables desde el archivo .env si existe temporalmente
load_dotenv()

def get_snowflake_credentials() -> dict:
    """Retorna un diccionario de configuración de Snowflake."""
    return {
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    }
