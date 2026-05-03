"""
Módulo para la conexión a Snowflake y extracción de datos iterativa (Big Data).
"""
import pandas as pd
import os
import sys
import snowflake.connector
from typing import Iterator

# Agregamos la ruta principal para que Python reconozca el paquete 'src' si corremos este script directamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.config import get_snowflake_credentials

def get_snowflake_connection():
    """Establece y retorna un objeto de conexión de Snowflake."""
    creds = get_snowflake_credentials()
    conn = snowflake.connector.connect(
        user=creds["user"],
        password=creds["password"],
        account=creds["account"],
        warehouse=creds["warehouse"],
        database=creds["database"],
        schema=creds["schema"]
    )
    return conn

def fetch_data_in_batches(query: str, batch_size: int = 100000) -> Iterator[pd.DataFrame]:
    """
    Extrae datos de Snowflake mediante cursores/lotes en lugar de cargar todo el DataFrame.
    Crucial para datasets de 20GB.
    
    Devuelve un iterador (yield) de pandas DataFrames para entrenamiento Out-of-Core.
    """
    conn = get_snowflake_connection()
    if conn is None:
        raise ConnectionError("No se pudo conectar a Snowflake.")
        
    # Ejecutar cursor.execute(query) 
    cursor = conn.cursor()
    cursor.execute(query)
    
    # Usar un bucle while True para llamar fetchmany(batch_size) o fetch_pandas_batches()
    for batch_df in cursor.fetch_pandas_batches():
        yield batch_df
        
    cursor.close()
    conn.close()

def fetch_sample(query: str, sample_prob: float = 1.0) -> pd.DataFrame:
    """Extrae una muestra única para experimentación en Jupyter (EDA)."""
    # Inyectar 'SAMPLE (sample_prob)' en el query y hacer fetchall() tradicional
    conn = get_snowflake_connection()
    if conn is None:
        raise ConnectionError("No se pudo conectar a Snowflake.")
        
    # Asumimos que el query termina sin punto y coma o lo manejamos
    query_with_sample = f"{query.strip(';')} SAMPLE ({sample_prob})"
    
    cursor = conn.cursor()
    cursor.execute(query_with_sample)
    df = cursor.fetch_pandas_all()
    cursor.close()
    conn.close()
    return df

def ingest_parquet_to_snowflake():
    """
    Descarga los archivos parquet en chunks (por mes) y los sube a Snowflake 
    usando pandas y snowflake-connector-python (write_pandas) sin necesidad de Spark.
    """
    import urllib.request
    from datetime import datetime, timezone
    from snowflake.connector.pandas_tools import write_pandas

    conn = get_snowflake_connection()
    if conn is None:
        raise ConnectionError("No se pudo conectar a Snowflake.")
    
    # Nos aseguramos de estar usando el schema correcto
    schema = os.getenv("SNOWFLAKE_SCHEMA_RAW", "RAW")
    conn.cursor().execute(f"USE SCHEMA {schema}")

    run_id = os.getenv("RUN_ID", "run_local_python_ingestion")
    
    años = range(2024, 2025)      
    meses = range(1, 2)         
    colores = ["yellow"]
    
    os.makedirs("data", exist_ok=True)
    temp_parquet = "data/current_batch.parquet"

    for color in colores:
        table_dest = "YELLOW_TRIPS_RAW" if color == "yellow" else "GREEN_TRIPS_RAW"
        for year in años:
            for month in meses:
                month_str = f"{month:02d}"
                url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{color}_tripdata_{year}-{month_str}.parquet"
                print(f"\n>>> Iniciando Ingesta: {color.upper()} {year}-{month_str}")
                
                try:
                    # Usamos un User-Agent de navegador para evitar bloqueos 403 (Forbidden)
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                    req = urllib.request.Request(url, headers=headers)
                    
                    with urllib.request.urlopen(req) as response, open(temp_parquet, 'wb') as out_file:
                        out_file.write(response.read())
                except Exception as e:
                    print(f"  [!] Archivo no encontrado o fallo al descargar (URL: {url}). Error: {e}")
                    continue
                
                try:
                    # Leer en pandas
                    df = pd.read_parquet(temp_parquet)
                    
                    # Mapa de renombrado para estandarizar los parquets crudos a nuestra BD
                    rename_map = {
                        'VendorID': 'VENDOR_ID',
                        'tpep_pickup_datetime': 'PICKUP_DATETIME',
                        'tpep_dropoff_datetime': 'DROPOFF_DATETIME',
                        'lpep_pickup_datetime': 'PICKUP_DATETIME',
                        'lpep_dropoff_datetime': 'DROPOFF_DATETIME',
                        'passenger_count': 'PASSENGER_COUNT',
                        'trip_distance': 'TRIP_DISTANCE',
                        'RatecodeID': 'RATE_CODE_ID',
                        'store_and_fwd_flag': 'STORE_AND_FWD_FLAG',
                        'PULocationID': 'PU_LOCATION_ID',
                        'DOLocationID': 'DO_LOCATION_ID',
                        'payment_type': 'PAYMENT_TYPE',
                        'fare_amount': 'FARE_AMOUNT',
                        'extra': 'EXTRA',
                        'mta_tax': 'MTA_TAX',
                        'tip_amount': 'TIP_AMOUNT',
                        'tolls_amount': 'TOLLS_AMOUNT',
                        'ehail_fee': 'EHAIL_FEE',
                        'improvement_surcharge': 'IMPROVEMENT_SURCHARGE',
                        'total_amount': 'TOTAL_AMOUNT',
                        'trip_type': 'TRIP_TYPE',
                        'congestion_surcharge': 'CONGESTION_SURCHARGE',
                        'airport_fee': 'AIRPORT_FEE',
                        'Airport_fee': 'AIRPORT_FEE'
                    }
                    
                    df = df.rename(columns=rename_map)
                    
                    # Si alguna columna no está en el mapa, y no es requerida, la pasamos a upper por precaución
                    df.columns = [str(c).upper() for c in df.columns]
                    
                    # Agregar columnas de metadatos (Pushdown al momento de subir)
                    df["RUN_ID"] = run_id
                    df["SOURCE_YEAR"] = year
                    df["SOURCE_MONTH"] = month
                    df["SERVICE_TYPE"] = color
                    df["INGESTED_AT_UTC"] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S.%f')
                    
                    # Formatear fechas explícitamente a string ISO para evitar problemas de parseo de Parquet en Snowflake ('Invalid date')
                    for date_col in ['PICKUP_DATETIME', 'DROPOFF_DATETIME']:
                        if date_col in df.columns:
                            # Convertimos a string conservando microsegundos, y si hay valores nulos los volvemos None reales
                            df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.strftime('%Y-%m-%d %H:%M:%S.%f')
                            df[date_col] = df[date_col].replace({pd.NA: None, 'NaT': None, 'nan': None})

                    
                    # Alinear con las columnas exactas de la tabla para que no falle write_pandas
                    if color == "yellow":
                        target_cols = ['VENDOR_ID', 'PICKUP_DATETIME', 'DROPOFF_DATETIME', 'PASSENGER_COUNT', 'TRIP_DISTANCE', 'RATE_CODE_ID', 'STORE_AND_FWD_FLAG', 'PU_LOCATION_ID', 'DO_LOCATION_ID', 'PAYMENT_TYPE', 'FARE_AMOUNT', 'EXTRA', 'MTA_TAX', 'TIP_AMOUNT', 'TOLLS_AMOUNT', 'IMPROVEMENT_SURCHARGE', 'TOTAL_AMOUNT', 'CONGESTION_SURCHARGE', 'AIRPORT_FEE', 'RUN_ID', 'SOURCE_YEAR', 'SOURCE_MONTH', 'SERVICE_TYPE', 'INGESTED_AT_UTC']
                    else:
                        target_cols = ['VENDOR_ID', 'PICKUP_DATETIME', 'DROPOFF_DATETIME', 'STORE_AND_FWD_FLAG', 'RATE_CODE_ID', 'PU_LOCATION_ID', 'DO_LOCATION_ID', 'PASSENGER_COUNT', 'TRIP_DISTANCE', 'FARE_AMOUNT', 'EXTRA', 'MTA_TAX', 'TIP_AMOUNT', 'TOLLS_AMOUNT', 'EHAIL_FEE', 'IMPROVEMENT_SURCHARGE', 'TOTAL_AMOUNT', 'PAYMENT_TYPE', 'TRIP_TYPE', 'CONGESTION_SURCHARGE', 'RUN_ID', 'SOURCE_YEAR', 'SOURCE_MONTH', 'SERVICE_TYPE', 'INGESTED_AT_UTC']
                    
                    # Nos quedamos solo con las columnas que acepta la tabla (descarta la columna basura que añadieron en 2025)
                    # Y rellenamos con None (nulo) las columnas que por algún motivo el mes no trajo
                    for tc in target_cols:
                        if tc not in df.columns:
                            df[tc] = None
                    df = df[target_cols]
                    
                    # Eliminar datos pre-existentes para idempotencia
                    delete_query = f"DELETE FROM {table_dest} WHERE source_year = {year} AND source_month = {month}"
                    conn.cursor().execute(delete_query)
                    
                    # Subir datos con write_pandas (muy optimizado y sin PySpark)
                    success, nchunks, nrows, _ = write_pandas(
                        conn=conn, 
                        df=df, 
                        table_name=table_dest,
                        auto_create_table=False
                    )
                    
                    if success:
                        print(f"  [v] Batch insertado exitosamente ({nrows} filas) en -> {table_dest}")
                    else:
                        print(f"  [!] Fallo parcial o total al insertar en -> {table_dest}")
                        
                except Exception as read_err:
                    print(f"  [!] Fallo en lectura/escritura: {read_err}")
                finally:
                    if os.path.exists(temp_parquet):
                        os.remove(temp_parquet)
                        
    conn.close()
    print("\n=======================================")
    print("INGESTA MASIVA DE 10 AÑOS FINALIZADA ")
    print("=======================================")

if __name__ == "__main__":
    ingest_parquet_to_snowflake()
