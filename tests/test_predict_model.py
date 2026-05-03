from src.models.predict_model import predict


class DummyModel:
    def predict(self, input_data):
        return [18.75 for _ in range(len(input_data))]


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

    preds = predict(DummyModel(), sample_trip)

    assert preds == [18.75]
