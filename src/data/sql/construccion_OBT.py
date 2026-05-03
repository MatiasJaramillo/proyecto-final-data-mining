"""Ejecuta los scripts SQL para crear RAW, OBT y splits temporales."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import snowflake.connector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.utils.config import get_snowflake_credentials


def run_sql_file(filepath: str, conn) -> None:
    full_path = PROJECT_ROOT / filepath
    sql_content = full_path.read_text(encoding="utf-8")

    statements = [statement.strip() for statement in sql_content.split(";") if statement.strip()]
    cursor = conn.cursor()
    try:
        for statement in statements:
            print(f"Executing: {statement[:80]}...")
            cursor.execute(statement)
    finally:
        cursor.close()


if __name__ == "__main__":
    creds = get_snowflake_credentials()
    conn = snowflake.connector.connect(
        user=creds["user"],
        password=creds["password"],
        account=creds["account"],
        warehouse=creds["warehouse"],
        role=creds.get("role") or os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
    )

    try:
        print("Running 00_create_raw_tables.sql...")
        run_sql_file("src/data/sql/00_create_raw_tables.sql", conn)

        print("Running 01_create_obt_and_split.sql...")
        run_sql_file("src/data/sql/01_create_obt_and_split.sql", conn)

        print("Setup complete!")
    finally:
        conn.close()
