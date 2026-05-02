"""
Servicio web rápido (FastAPI) para servir el modelo empaquetado.
"""
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
# from src.models.predict_model import load_model, predict

app = FastAPI(title="API - Predicción de Precios ML", version="1.0")

# TODO: Define el esquema de Pydantic según lo que el modelo va a recibir
class TripInput(BaseModel):
    passenger_count: int
    trip_distance: float
    # ... Añadir resto de los features

@app.on_event("startup")
def load_artifacts():
    """Ejecutado al iniciar el servidor FastAPI. Usado para dejar en caché el modelo."""
    # TODO: model = load_model('ruta/al/modelo.pkl')
    pass

@app.post("/predict")
def predict_price(trip: TripInput):
    """Endpoint para predecir total_amount del viaje entrante."""
    # TODO: Mapear el TripInput a un pandas DataFrame
    # TODO: Llamar la función predict y devolver el resultado
    return {"estimated_total_amount": 0.0}
