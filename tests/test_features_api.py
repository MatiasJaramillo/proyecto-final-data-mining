import pandas as pd
from fastapi.testclient import TestClient

from src.api import main
from src.features.build_features import preprocess_data


class DummyModel:
    def predict(self, input_data):
        return [12.34 for _ in range(len(input_data))]


def test_preprocess_removes_leakage_and_creates_temporal_features():
    raw = pd.DataFrame(
        [
            {
                "pickup_datetime": "2025-01-18T08:30:00",
                "passenger_count": 1,
                "trip_distance": 2.5,
                "trip_duration_min": 15,
                "fare_amount": 9.5,
                "total_amount": 14.0,
            }
        ]
    )

    result = preprocess_data(raw)

    assert "fare_amount" not in result.columns
    assert "total_amount" in result.columns
    assert result.loc[0, "pickup_hour"] == 8
    assert result.loc[0, "is_weekend"] == 1
    assert "trip_duration_min" not in result.columns


def test_predict_endpoint_returns_model_prediction(monkeypatch):
    monkeypatch.setattr(main, "model", DummyModel())
    client = TestClient(main.app)

    response = client.post(
        "/predict",
        json={
            "vendor_id": 1,
            "pickup_datetime": "2025-01-15T08:30:00",
            "passenger_count": 1,
            "trip_distance": 2.5,
            "trip_duration_min": 15,
            "rate_code_id": 1,
            "pu_location_id": 132,
            "do_location_id": 236,
            "payment_type": 1,
            "taxi_type": "yellow",
        },
    )

    assert response.status_code == 200
    assert response.json()["estimated_total_amount"] == 12.34
