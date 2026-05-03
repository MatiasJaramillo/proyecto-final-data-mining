CREATE DATABASE IF NOT EXISTS ANALYTICS;
USE DATABASE ANALYTICS;

CREATE SCHEMA IF NOT EXISTS RAW;
USE SCHEMA RAW;

CREATE TABLE IF NOT EXISTS YELLOW_TRIPS_RAW (
    vendor_id INTEGER,
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    passenger_count FLOAT,
    trip_distance FLOAT,
    rate_code_id FLOAT,
    store_and_fwd_flag STRING,
    pu_location_id INTEGER,
    do_location_id INTEGER,
    payment_type FLOAT,
    fare_amount FLOAT,
    extra FLOAT,
    mta_tax FLOAT,
    tip_amount FLOAT,
    tolls_amount FLOAT,
    improvement_surcharge FLOAT,
    total_amount FLOAT,
    congestion_surcharge FLOAT,
    airport_fee FLOAT,
    run_id STRING,
    source_year INTEGER,
    source_month INTEGER,
    service_type STRING,
    ingested_at_utc TIMESTAMP
);

CREATE TABLE IF NOT EXISTS GREEN_TRIPS_RAW (
    vendor_id INTEGER,
    pickup_datetime TIMESTAMP,
    dropoff_datetime TIMESTAMP,
    store_and_fwd_flag STRING,
    rate_code_id FLOAT,
    pu_location_id INTEGER,
    do_location_id INTEGER,
    passenger_count FLOAT,
    trip_distance FLOAT,
    fare_amount FLOAT,
    extra FLOAT,
    mta_tax FLOAT,
    tip_amount FLOAT,
    tolls_amount FLOAT,
    ehail_fee FLOAT,
    improvement_surcharge FLOAT,
    total_amount FLOAT,
    payment_type FLOAT,
    trip_type FLOAT,
    congestion_surcharge FLOAT,
    run_id STRING,
    source_year INTEGER,
    source_month INTEGER,
    service_type STRING,
    ingested_at_utc TIMESTAMP
);
