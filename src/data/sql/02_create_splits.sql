-- ==========================================
-- 02: Separación Temporal (Data Splits)
-- ==========================================
-- Los conjuntos de entrenamiento, validación y prueba NO se crearán 
-- en la máquina local usando train_test_split. Se materializarán en Snowflake.

-- Escribir el SQL para crear vistas o tablas separadas 
-- con base a los años analizados. 
-- * Train: 2015-2023
-- * Validación: 2024
-- * Test: 2025

-- Ejemplos sugeridos:
-- CREATE OR REPLACE VIEW analytics.train_set AS
-- SELECT * FROM analytics.obt_trips_model 
-- WHERE EXTRACT(YEAR FROM pickup_datetime) <= 2023;

-- CREATE OR REPLACE VIEW analytics.val_set AS ...
-- CREATE OR REPLACE VIEW analytics.test_set AS ...
