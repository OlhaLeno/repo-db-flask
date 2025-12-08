-- Sample queries to get data from database for report screenshots
-- Execute these in Azure Portal Query Editor

-- =============================================
-- 1. Get recent sensor readings (last 10)
-- =============================================
SELECT TOP 10
    id,
    sensor_id,
    sensor_type,
    value,
    latitude,
    longitude,
    timestamp,
    created_at
FROM sensor_data
ORDER BY timestamp DESC;

-- =============================================
-- 2. Get statistics by sensor type
-- =============================================
SELECT 
    sensor_type,
    COUNT(*) as total_readings,
    AVG(value) as avg_value,
    MIN(value) as min_value,
    MAX(value) as max_value,
    MIN(timestamp) as first_reading,
    MAX(timestamp) as last_reading
FROM sensor_data
GROUP BY sensor_type
ORDER BY sensor_type;

-- =============================================
-- 3. Get readings count by sensor
-- =============================================
SELECT 
    sensor_id,
    sensor_type,
    COUNT(*) as reading_count,
    AVG(value) as avg_value
FROM sensor_data
GROUP BY sensor_id, sensor_type
ORDER BY reading_count DESC;

-- =============================================
-- 4. Get DLQ errors (if any exist)
-- =============================================
SELECT TOP 10
    id,
    message_id,
    sensor_id,
    sensor_type,
    error_type,
    error_category,
    status,
    dead_lettered_time,
    recovery_attempts
FROM dlq_errors
ORDER BY dead_lettered_time DESC;

-- =============================================
-- 5. Get DLQ statistics summary
-- =============================================
SELECT 
    COUNT(*) as total_errors,
    SUM(CASE WHEN error_type = 'transient' THEN 1 ELSE 0 END) as transient_errors,
    SUM(CASE WHEN error_type = 'validation' THEN 1 ELSE 0 END) as validation_errors,
    SUM(CASE WHEN error_type = 'business' THEN 1 ELSE 0 END) as business_errors,
    SUM(CASE WHEN error_type = 'system' THEN 1 ELSE 0 END) as system_errors,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
    SUM(CASE WHEN status = 'recovered' THEN 1 ELSE 0 END) as recovered_count
FROM dlq_errors;

-- =============================================
-- 6. Get recent readings with formatted output (for screenshot)
-- =============================================
SELECT TOP 5
    sensor_id AS 'Датчик',
    sensor_type AS 'Тип',
    CAST(value AS DECIMAL(10,2)) AS 'Значення',
    CAST(latitude AS DECIMAL(10,6)) AS 'Широта',
    CAST(longitude AS DECIMAL(11,6)) AS 'Довгота',
    FORMAT(timestamp, 'yyyy-MM-dd HH:mm:ss') AS 'Час'
FROM sensor_data
ORDER BY timestamp DESC;

-- =============================================
-- 7. Get hourly statistics (last 24 hours)
-- =============================================
SELECT 
    DATEPART(HOUR, timestamp) as hour,
    sensor_type,
    COUNT(*) as reading_count,
    AVG(value) as avg_value
FROM sensor_data
WHERE timestamp >= DATEADD(HOUR, -24, GETUTCDATE())
GROUP BY DATEPART(HOUR, timestamp), sensor_type
ORDER BY hour, sensor_type;

