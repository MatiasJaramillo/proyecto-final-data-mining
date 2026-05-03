"""Utilidades para cargar variables de entorno y configuracion central."""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def _load_env_fallback() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


if load_dotenv is not None:
    load_dotenv()
else:
    _load_env_fallback()


def get_snowflake_credentials() -> dict:
    """Retorna la configuracion de conexion a Snowflake."""
    schema = os.getenv("SNOWFLAKE_SCHEMA") or os.getenv("SNOWFLAKE_SCHEMA_RAW")
    return {
        "user": os.getenv("SNOWFLAKE_USER"),
        "password": os.getenv("SNOWFLAKE_PASSWORD"),
        "account": os.getenv("SNOWFLAKE_ACCOUNT"),
        "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
        "database": os.getenv("SNOWFLAKE_DATABASE"),
        "schema": schema,
        "role": os.getenv("SNOWFLAKE_ROLE"),
    }
