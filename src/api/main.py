from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

from src.models.predict_model import predict


app = FastAPI(title="Taxi Price Prediction API")


# Input schema (what frontend sends)
class TripInput(BaseModel):
    vendor_id: int
    passenger_count: int
    trip_distance: float
    rate_code_id: int
    pu_location_id: int
    do_location_id: int
    service_type: str
    pickup_datetime: str


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/predict")
def predict_price(trip: TripInput):
    input_df = pd.DataFrame([trip.model_dump()])

    prediction = predict(input_df)

    return {
        "predicted_price": float(prediction[0])
    }