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

import pandas as pd

# Diccionarios de mapeo para mejorar la experiencia de usuario
providers = {
    1: "1 - Creative Mobile Technologies, LLC",
    2: "2 - Curb Mobility, LLC",
}

rate_codes = {
    1: "1 - Standard rate",
    2: "2 - JFK",
    3: "3 - Newark",
    4: "4 - Nassau or Westchester",
    5: "5 - Negotiated fare",
    6: "6 - Group ride",
    99: "99 - Null/unknown"
}

payment_methods = {
    1: "1 - Credit card",
    2: "2 - Cash",
    3: "3 - No charge",
    4: "4 - Dispute",
    5: "5 - Unknown",
    6: "6 - Voided trip"
}

# Cargar zonas desde CSV
try:
    zones_df = pd.read_csv('app/data/taxi_zone_lookup (1).csv')
    zones_dict = {row['LocationID']: f"{row['LocationID']} - {row['Borough']}: {row['Zone']}" for _, row in zones_df.iterrows()}
except Exception:
    # Fallback por si no encuentra el archivo
    zones_dict = {i: f"Zona {i}" for i in range(1, 266)}
    zones_dict[132] = "132 - Queens: JFK Airport"
    zones_dict[236] = "236 - Manhattan: Upper East Side North"

st.subheader("Datos del viaje")

with st.form("trip_form"):
    col_left, col_right = st.columns(2)

    with col_left:
        taxi_type = st.selectbox("Tipo de taxi", ["yellow", "green"])
        vendor_id = st.selectbox("Proveedor", options=list(providers.keys()), format_func=lambda x: providers[x])
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
        rate_code_id = st.selectbox("Rate code", options=list(rate_codes.keys()), format_func=lambda x: rate_codes[x])
        
        # Encontrar los indices por defecto para JFK (132) y UES (236) si existen en las llaves
        keys_list = list(zones_dict.keys())
        idx_origen = keys_list.index(132) if 132 in keys_list else 0
        idx_destino = keys_list.index(236) if 236 in keys_list else 0
        
        pu_location_id = st.selectbox("Zona origen", options=keys_list, index=idx_origen, format_func=lambda x: zones_dict[x])
        do_location_id = st.selectbox("Zona destino", options=keys_list, index=idx_destino, format_func=lambda x: zones_dict[x])
        payment_type = st.selectbox("Metodo de pago", options=list(payment_methods.keys()), index=1, format_func=lambda x: payment_methods[x])

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
