-- Create table for IoT sensor data (if not exists)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'sensor_data')
BEGIN
    CREATE TABLE sensor_data (
        id BIGINT PRIMARY KEY IDENTITY(1,1),
        sensor_id VARCHAR(50) NOT NULL,
        sensor_type VARCHAR(20) NOT NULL,
        value DECIMAL(10,2) NOT NULL,
        latitude DECIMAL(10,8) NOT NULL,
        longitude DECIMAL(11,8) NOT NULL,
        timestamp DATETIME2 NOT NULL,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE()
    );
    PRINT 'Table sensor_data created successfully';
END
ELSE
BEGIN
    PRINT 'Table sensor_data already exists';
END

-- Indexes for fast search (if not exist)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_sensor_type' AND object_id = OBJECT_ID('sensor_data'))
BEGIN
    CREATE INDEX idx_sensor_type ON sensor_data(sensor_type);
    PRINT 'Index idx_sensor_type created';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_timestamp' AND object_id = OBJECT_ID('sensor_data'))
BEGIN
    CREATE INDEX idx_timestamp ON sensor_data(timestamp);
    PRINT 'Index idx_timestamp created';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_sensor_id' AND object_id = OBJECT_ID('sensor_data'))
BEGIN
    CREATE INDEX idx_sensor_id ON sensor_data(sensor_id);
    PRINT 'Index idx_sensor_id created';
END

-- Verify table creation
SELECT TABLE_NAME, TABLE_TYPE 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_NAME = 'sensor_data';

