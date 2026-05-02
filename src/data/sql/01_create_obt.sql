-- ==========================================
-- 01: Construcción de la One Big Table (OBT)
-- ==========================================
-- Como el volumen de datos es ~20GB, NO exportaremos múltiples tablas a Python.
-- Toda la lógica de "joinear" o agregar debe correr en el clúster de Snowflake.

-- Escribir el DDL/DML para crear o reemplazar la tabla materializada 
-- `analytics.obt_trips_model` cruzando `yellow_trips` y `green_trips` si aplica,
-- o aplicando selecciones tempranas.

-- USE WAREHOUSE COMPUTE_WH;
-- USE DATABASE ANALYTICS;

-- CREATE OR REPLACE TABLE analytics.obt_trips_model AS 
-- SELECT 
--     *
-- FROM source_trips
-- WHERE ...
