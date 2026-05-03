"""API FastAPI para servir predicciones de precio de viajes NYC Taxi."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.models.predict_model import DEFAULT_MODEL_PATH, LEGACY_MODEL_PATH, load_model, predict


ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_API_MODEL_PATH = ROOT_DIR / DEFAULT_MODEL_PATH
LEGACY_API_MODEL_PATH = ROOT_DIR / LEGACY_MODEL_PATH

model = None
model_path = Path(os.getenv("MODEL_PATH", DEFAULT_API_MODEL_PATH))
if not model_path.exists() and LEGACY_API_MODEL_PATH.exists():
    model_path = LEGACY_API_MODEL_PATH


def load_artifacts():
    """Carga el modelo al iniciar el servidor y lo mantiene en cache."""
    global model
    if model_path.exists():
        model = load_model(model_path)


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    load_artifacts()
    yield


app = FastAPI(
    title="API - Prediccion de Precios ML",
    version="1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TripInput(BaseModel):
    vendor_id: int = Field(1, ge=1, le=2)
    pickup_datetime: datetime
    passenger_count: int = Field(1, ge=0, le=9)
    trip_distance: float = Field(..., gt=0, le=150)
    trip_duration_min: float = Field(..., gt=0, le=1440)
    rate_code_id: int = Field(1, ge=1, le=99)
    pu_location_id: int = Field(..., ge=1, le=265)
    do_location_id: int = Field(..., ge=1, le=265)
    payment_type: int = Field(1, ge=1, le=6)
    taxi_type: str = Field("yellow", pattern="^(yellow|green)$")


class PredictionResponse(BaseModel):
    estimated_total_amount: float
    currency: str = "USD"
    model_path: str


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "model_path": str(model_path),
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_price(trip: TripInput):
    """Endpoint para predecir total_amount del viaje entrante."""
    if model is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Modelo no cargado. Entrena/exporta el .pkl o define MODEL_PATH "
                f"apuntando al archivo correcto. Ruta actual: {model_path}"
            ),
        )

    input_df = pd.DataFrame(
        [
            {
                "vendor_id": trip.vendor_id,
                "pickup_datetime": trip.pickup_datetime,
                "passenger_count": trip.passenger_count,
                "trip_distance": trip.trip_distance,
                "trip_duration_min": trip.trip_duration_min,
                "rate_code_id": trip.rate_code_id,
                "pu_location_id": trip.pu_location_id,
                "do_location_id": trip.do_location_id,
                "payment_type": trip.payment_type,
                "taxi_type": trip.taxi_type,
                "service_type": trip.taxi_type,
            }
        ]
    )
    prediction = predict(model, input_df)[0]
    return {
        "estimated_total_amount": round(prediction, 2),
        "currency": "USD",
        "model_path": str(model_path),
    }
