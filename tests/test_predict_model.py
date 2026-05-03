import numpy as np
from src.models.predict_model import predict


def test_predict_single_sample():
    sample_trip = {
        "vendor_id": 1,
        "passenger_count": 1,
        "trip_distance": 2.5,
        "rate_code_id": 1,
        "pu_location_id": 161,
        "do_location_id": 236,
        "service_type": "yellow",
        "pickup_datetime": "2025-01-15 14:30:00",
    }

    preds = predict(sample_trip)

    # Check shape
    assert isinstance(preds, np.ndarray)
    assert preds.shape == (1,)

    # Check value makes sense
    assert preds[0] > 0