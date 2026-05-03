from datetime import datetime, time

import requests
import streamlit as st


API_BASE_URL = "http://127.0.0.1:8000"
PREDICT_URL = f"{API_BASE_URL}/predict"

st.set_page_config(page_title="Prediccion de tarifa NYC Taxi")

st.title("Prediccion de tarifa NYC Taxi")
st.caption("Interfaz Streamlit conectada a la API FastAPI del modelo final.")

with st.sidebar:
    st.header("Estado de la API")
    if st.button("Verificar conexion"):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            response.raise_for_status()
            health = response.json()
            if health.get("model_loaded"):
                st.success("API activa con modelo cargado.")
            else:
                st.warning("API activa, pero falta cargar el .pkl.")
            st.code(health.get("model_path", ""))
        except requests.RequestException as exc:
            st.error(f"No se pudo conectar con FastAPI: {exc}")

st.subheader("Datos del viaje")

with st.form("trip_form"):
    col_left, col_right = st.columns(2)

    with col_left:
        taxi_type = st.selectbox("Tipo de taxi", ["yellow", "green"])
        vendor_id = st.selectbox("Proveedor", [1, 2])
        passenger_count = st.number_input("Pasajeros", min_value=0, max_value=9, value=1, step=1)
        trip_distance = st.number_input(
            "Distancia (millas)",
            min_value=0.01,
            max_value=150.0,
            value=2.5,
            step=0.1,
        )
        trip_duration_min = st.number_input(
            "Duracion estimada (min)",
            min_value=1.0,
            max_value=1440.0,
            value=15.0,
            step=1.0,
        )

    with col_right:
        pickup_date = st.date_input("Fecha de recogida")
        pickup_time = st.time_input("Hora de recogida", value=time(8, 30))
        rate_code_id = st.number_input("Rate code", min_value=1, max_value=99, value=1, step=1)
        pu_location_id = st.number_input("Zona origen", min_value=1, max_value=265, value=132, step=1)
        do_location_id = st.number_input("Zona destino", min_value=1, max_value=265, value=236, step=1)
        payment_type = st.selectbox("Metodo de pago", [1, 2, 3, 4, 5, 6])

    submitted = st.form_submit_button("Predecir tarifa")

if submitted:
    pickup_datetime = datetime.combine(pickup_date, pickup_time)
    payload = {
        "vendor_id": vendor_id,
        "pickup_datetime": pickup_datetime.isoformat(),
        "passenger_count": passenger_count,
        "trip_distance": trip_distance,
        "trip_duration_min": trip_duration_min,
        "rate_code_id": rate_code_id,
        "pu_location_id": pu_location_id,
        "do_location_id": do_location_id,
        "payment_type": payment_type,
        "taxi_type": taxi_type,
    }

    try:
        response = requests.post(PREDICT_URL, json=payload, timeout=15)
        response.raise_for_status()
        result = response.json()
        st.metric(
            "Tarifa estimada",
            f"${result['estimated_total_amount']:.2f} {result['currency']}",
        )
    except requests.HTTPError as exc:
        detail = response.json().get("detail", str(exc))
        st.error(detail)
    except requests.RequestException as exc:
        st.error(f"No se pudo conectar con la API: {exc}")
