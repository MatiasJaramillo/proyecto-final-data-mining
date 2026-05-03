CREATE SCHEMA IF NOT EXISTS ANALYTICS.REFINED;
USE SCHEMA ANALYTICS.REFINED;

-- Materialización de la One Big Table (OBT) uniendo viajes amarillos y verdes con LIMPIEZA
CREATE OR REPLACE TABLE OBT_TRIPS AS
WITH consolidated_raw AS (
    SELECT 
        vendor_id, pickup_datetime, dropoff_datetime, passenger_count, trip_distance, 
        rate_code_id, store_and_fwd_flag, pu_location_id, do_location_id, payment_type, 
        fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, 
        total_amount, congestion_surcharge, airport_fee, NULL AS ehail_fee, NULL AS trip_type, 
        source_year, source_month, service_type, run_id, ingested_at_utc
    FROM ANALYTICS.RAW.YELLOW_TRIPS_RAW
    UNION ALL
    SELECT 
        vendor_id, pickup_datetime, dropoff_datetime, passenger_count, trip_distance, 
        rate_code_id, store_and_fwd_flag, pu_location_id, do_location_id, payment_type, 
        fare_amount, extra, mta_tax, tip_amount, tolls_amount, improvement_surcharge, 
        total_amount, congestion_surcharge, NULL AS airport_fee, ehail_fee, trip_type, 
        source_year, source_month, service_type, run_id, ingested_at_utc
    FROM ANALYTICS.RAW.GREEN_TRIPS_RAW
)
SELECT 
    *,
    -- Feature Engineering Base
    ROUND(DATEDIFF('second', pickup_datetime, dropoff_datetime) / 60.0, 2) AS trip_duration_min,
    CASE 
        WHEN DATEDIFF('second', pickup_datetime, dropoff_datetime) > 0 AND trip_distance > 0 
        THEN ROUND(trip_distance / (DATEDIFF('second', pickup_datetime, dropoff_datetime) / 3600.0), 2)
        ELSE NULL 
    END AS avg_speed_mph,
    CASE 
        WHEN fare_amount > 0 THEN ROUND((tip_amount / fare_amount) * 100.0, 2)
        ELSE NULL 
    END AS tip_pct
FROM consolidated_raw
WHERE 
    -- Validacion 1: Fechas no nulas
    pickup_datetime IS NOT NULL AND dropoff_datetime IS NOT NULL
    -- Validacion 2: Consistencia temporal (el viaje pertenece al archivo cargado)
    AND EXTRACT(YEAR FROM pickup_datetime) = source_year
    AND EXTRACT(MONTH FROM pickup_datetime) = source_month
    -- Validacion 3: Distancia positiva
    AND trip_distance > 0
    -- Validacion 4: No tarifas negativas
    AND fare_amount >= 0 AND total_amount >= 0
    -- Validacion 5: Duracion positiva
    AND DATEDIFF('second', pickup_datetime, dropoff_datetime) > 0
    -- Validacion 6: Pasajeros realistas
    AND COALESCE(passenger_count, 0) BETWEEN 0 AND 9
    -- Validacion 7: Control de velocidad (evitar outliers absurdos > 150 mph)
    AND (trip_distance / NULLIF(DATEDIFF('second', pickup_datetime, dropoff_datetime), 0) * 3600 <= 150);

-- Creación de la partición temporal para el equipo de ML
-- Train 2015-2023
CREATE OR REPLACE VIEW OBT_TRIPS_TRAIN AS
SELECT * FROM OBT_TRIPS WHERE source_year BETWEEN 2015 AND 2023;

-- Val 2024
CREATE OR REPLACE VIEW OBT_TRIPS_VAL AS
SELECT * FROM OBT_TRIPS WHERE source_year = 2024;

-- Test 2025
CREATE OR REPLACE VIEW OBT_TRIPS_TEST AS
SELECT * FROM OBT_TRIPS WHERE source_year = 2025;
