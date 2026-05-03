import os
import sys
import snowflake.connector

# Ajustamos la ruta para que encuentre 'src' desde la carpeta 'src/data/sql'
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.config import get_snowflake_credentials

def run_sql_file(filepath, conn):
    # Ajustamos la ruta base ya que el script se corre desde la raíz o desde sql/
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    full_path = os.path.join(base_dir, filepath)
    
    with open(full_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Simple split by ';' for multiple statements
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]
    cursor = conn.cursor()
    for statement in statements:
        print(f"Executing: {statement[:50]}...")
        cursor.execute(statement)
    cursor.close()

if __name__ == "__main__":
    creds = get_snowflake_credentials()
    # Connect without db/schema first to ensure we can create them
    conn = snowflake.connector.connect(
        user=creds["user"],
        password=creds["password"],
        account=creds["account"],
        warehouse=creds["warehouse"],
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
    )
    
    print("Running 00_create_raw_tables.sql...")
    run_sql_file("src/data/sql/00_create_raw_tables.sql", conn)
    
    print("Running 01_create_obt_and_split.sql...")
    run_sql_file("src/data/sql/01_create_obt_and_split.sql", conn)
    
    print("Setup complete!")
    conn.close()
