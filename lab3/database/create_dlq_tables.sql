-- =============================================
-- Dead Letter Queue Tables
-- =============================================
-- Creates tables for Dead Letter Queue processing
-- Execute in iot-sensors-db database context

USE [iot-sensors-db];
GO

-- =============================================
-- 1. Table for DLQ errors
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dlq_errors')
BEGIN
    CREATE TABLE dlq_errors (
        id INT IDENTITY(1,1) PRIMARY KEY,
        message_id NVARCHAR(255) NOT NULL,
        enqueued_time DATETIME2 NOT NULL,
        dead_lettered_time DATETIME2 DEFAULT GETUTCDATE(),
        
        -- Original data
        original_message NVARCHAR(MAX) NOT NULL,
        sensor_id NVARCHAR(100),
        sensor_type NVARCHAR(50),
        
        -- Error information
        error_type NVARCHAR(50) NOT NULL, -- 'transient', 'validation', 'business', 'system'
        error_category NVARCHAR(100), -- 'db_connection', 'invalid_json', 'duplicate', etc.
        error_message NVARCHAR(MAX),
        error_details NVARCHAR(MAX),
        stack_trace NVARCHAR(MAX),
        
        -- Service Bus metadata
        delivery_count INT,
        dead_letter_reason NVARCHAR(255),
        dead_letter_error_description NVARCHAR(MAX),
        
        -- Processing status
        status NVARCHAR(50) DEFAULT 'pending', -- 'pending', 'analyzed', 'recovered', 'archived', 'failed'
        recovery_attempts INT DEFAULT 0,
        last_recovery_attempt DATETIME2,
        resolved_time DATETIME2,
        resolved_by NVARCHAR(100),
        resolution_notes NVARCHAR(MAX),
        
        created_at DATETIME2 DEFAULT GETUTCDATE(),
        updated_at DATETIME2 DEFAULT GETUTCDATE()
    );
    
    -- Indexes for query optimization
    CREATE INDEX IX_dlq_errors_dead_lettered_time ON dlq_errors(dead_lettered_time DESC);
    CREATE INDEX IX_dlq_errors_error_type ON dlq_errors(error_type);
    CREATE INDEX IX_dlq_errors_status ON dlq_errors(status);
    CREATE INDEX IX_dlq_errors_sensor_type ON dlq_errors(sensor_type);
    CREATE INDEX IX_dlq_errors_message_id ON dlq_errors(message_id);
    CREATE INDEX IX_dlq_errors_sensor_id ON dlq_errors(sensor_id);
    
    PRINT 'Table dlq_errors created successfully';
END
ELSE
BEGIN
    PRINT 'Table dlq_errors already exists';
END
GO

-- =============================================
-- 2. Recovery history table
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dlq_recovery')
BEGIN
    CREATE TABLE dlq_recovery (
        id INT IDENTITY(1,1) PRIMARY KEY,
        dlq_error_id INT NOT NULL,
        recovery_time DATETIME2 DEFAULT GETUTCDATE(),
        recovery_method NVARCHAR(100), -- 'auto_retry', 'manual_fix', 'data_correction', 'requeue'
        recovery_status NVARCHAR(50) NOT NULL, -- 'success', 'failed', 'partial'
        modified_message NVARCHAR(MAX),
        recovery_notes NVARCHAR(MAX),
        error_on_recovery NVARCHAR(MAX),
        performed_by NVARCHAR(100),
        
        CONSTRAINT FK_dlq_recovery_error FOREIGN KEY (dlq_error_id) 
            REFERENCES dlq_errors(id) ON DELETE CASCADE
    );
    
    -- Indexes
    CREATE INDEX IX_dlq_recovery_error_id ON dlq_recovery(dlq_error_id);
    CREATE INDEX IX_dlq_recovery_time ON dlq_recovery(recovery_time DESC);
    CREATE INDEX IX_dlq_recovery_status ON dlq_recovery(recovery_status);
    
    PRINT 'Table dlq_recovery created successfully';
END
ELSE
BEGIN
    PRINT 'Table dlq_recovery already exists';
END
GO

-- =============================================
-- 3. DLQ statistics table
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dlq_statistics')
BEGIN
    CREATE TABLE dlq_statistics (
        id INT IDENTITY(1,1) PRIMARY KEY,
        date DATE NOT NULL,
        hour TINYINT NOT NULL CHECK (hour >= 0 AND hour <= 23),
        
        -- Error metrics
        total_dead_lettered INT DEFAULT 0,
        error_type_transient INT DEFAULT 0,
        error_type_validation INT DEFAULT 0,
        error_type_business INT DEFAULT 0,
        error_type_system INT DEFAULT 0,
        
        -- Recovery metrics
        successful_recoveries INT DEFAULT 0,
        failed_recoveries INT DEFAULT 0,
        pending_recoveries INT DEFAULT 0,
        
        -- Sensor metrics
        affected_sensors NVARCHAR(MAX), -- JSON array of sensor_ids
        affected_sensor_types NVARCHAR(MAX), -- JSON array of sensor_types
        
        -- Error category metrics
        error_categories NVARCHAR(MAX), -- JSON object with counts
        
        created_at DATETIME2 DEFAULT GETUTCDATE(),
        updated_at DATETIME2 DEFAULT GETUTCDATE(),
        
        CONSTRAINT UQ_dlq_statistics_date_hour UNIQUE (date, hour)
    );
    
    -- Indexes
    CREATE INDEX IX_dlq_statistics_date ON dlq_statistics(date DESC);
    CREATE INDEX IX_dlq_statistics_date_hour ON dlq_statistics(date DESC, hour DESC);
    
    PRINT 'Table dlq_statistics created successfully';
END
ELSE
BEGIN
    PRINT 'Table dlq_statistics already exists';
END
GO

-- =============================================
-- 4. DLQ alerts table
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dlq_alerts')
BEGIN
    CREATE TABLE dlq_alerts (
        id INT IDENTITY(1,1) PRIMARY KEY,
        alert_time DATETIME2 DEFAULT GETUTCDATE(),
        alert_type NVARCHAR(50) NOT NULL, -- 'critical', 'warning', 'info'
        alert_category NVARCHAR(100) NOT NULL, -- 'high_volume', 'system_error', 'recovery_failure', etc.
        alert_message NVARCHAR(MAX) NOT NULL,
        alert_details NVARCHAR(MAX),
        
        -- Metadata
        dlq_error_id INT,
        affected_count INT,
        threshold_value DECIMAL(10,2),
        current_value DECIMAL(10,2),
        
        -- Processing status
        status NVARCHAR(50) DEFAULT 'new', -- 'new', 'acknowledged', 'resolved', 'ignored'
        acknowledged_by NVARCHAR(100),
        acknowledged_at DATETIME2,
        resolved_at DATETIME2,
        resolution_notes NVARCHAR(MAX),
        
        CONSTRAINT FK_dlq_alerts_error FOREIGN KEY (dlq_error_id) 
            REFERENCES dlq_errors(id) ON DELETE SET NULL
    );
    
    -- Indexes
    CREATE INDEX IX_dlq_alerts_time ON dlq_alerts(alert_time DESC);
    CREATE INDEX IX_dlq_alerts_type ON dlq_alerts(alert_type);
    CREATE INDEX IX_dlq_alerts_status ON dlq_alerts(status);
    
    PRINT 'Table dlq_alerts created successfully';
END
ELSE
BEGIN
    PRINT 'Table dlq_alerts already exists';
END
GO

-- =============================================
-- Stored Procedures for DLQ operations
-- =============================================

-- Procedure to get DLQ statistics
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_get_dlq_statistics')
    DROP PROCEDURE sp_get_dlq_statistics;
GO

CREATE PROCEDURE sp_get_dlq_statistics
    @time_period NVARCHAR(10) = '24h' -- '1h', '24h', '7d', '30d', 'all'
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @cutoff_time DATETIME2;
    
    -- Determine cutoff time
    IF @time_period = '1h'
        SET @cutoff_time = DATEADD(HOUR, -1, GETUTCDATE());
    ELSE IF @time_period = '24h'
        SET @cutoff_time = DATEADD(HOUR, -24, GETUTCDATE());
    ELSE IF @time_period = '7d'
        SET @cutoff_time = DATEADD(DAY, -7, GETUTCDATE());
    ELSE IF @time_period = '30d'
        SET @cutoff_time = DATEADD(DAY, -30, GETUTCDATE());
    ELSE
        SET @cutoff_time = '1900-01-01'; -- all
    
    -- Overall statistics
    SELECT 
        COUNT(*) as total_errors,
        SUM(CASE WHEN error_type = 'transient' THEN 1 ELSE 0 END) as transient_errors,
        SUM(CASE WHEN error_type = 'validation' THEN 1 ELSE 0 END) as validation_errors,
        SUM(CASE WHEN error_type = 'business' THEN 1 ELSE 0 END) as business_errors,
        SUM(CASE WHEN error_type = 'system' THEN 1 ELSE 0 END) as system_errors,
        SUM(CASE WHEN status = 'recovered' THEN 1 ELSE 0 END) as recovered_count,
        SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_count,
        AVG(DATEDIFF(MINUTE, dead_lettered_time, COALESCE(resolved_time, GETUTCDATE()))) as avg_resolution_time_minutes,
        MIN(dead_lettered_time) as first_error_time,
        MAX(dead_lettered_time) as last_error_time
    FROM dlq_errors
    WHERE dead_lettered_time >= @cutoff_time;
    
    -- Top errors by category
    SELECT TOP 10
        error_category,
        COUNT(*) as error_count,
        error_type,
        MAX(dead_lettered_time) as last_occurrence
    FROM dlq_errors
    WHERE dead_lettered_time >= @cutoff_time
    GROUP BY error_category, error_type
    ORDER BY error_count DESC;
    
    -- Top problematic sensors
    SELECT TOP 10
        sensor_id,
        sensor_type,
        COUNT(*) as error_count,
        MAX(dead_lettered_time) as last_error
    FROM dlq_errors
    WHERE dead_lettered_time >= @cutoff_time
        AND sensor_id IS NOT NULL
    GROUP BY sensor_id, sensor_type
    ORDER BY error_count DESC;
END
GO

PRINT 'Stored procedure sp_get_dlq_statistics created successfully';
GO

-- Procedure to cleanup old DLQ records
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_cleanup_dlq_errors')
    DROP PROCEDURE sp_cleanup_dlq_errors;
GO

CREATE PROCEDURE sp_cleanup_dlq_errors
    @retention_days INT = 90
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @cutoff_date DATETIME2;
    SET @cutoff_date = DATEADD(DAY, -@retention_days, GETUTCDATE());
    
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Delete old records (recovered or archived)
        DELETE FROM dlq_errors
        WHERE dead_lettered_time < @cutoff_date
            AND status IN ('recovered', 'archived');
        
        DECLARE @deleted_count INT = @@ROWCOUNT;
        
        -- Archive very old pending records
        UPDATE dlq_errors
        SET status = 'archived',
            resolution_notes = 'Auto-archived due to age (' + CAST(@retention_days AS NVARCHAR) + ' days)'
        WHERE dead_lettered_time < @cutoff_date
            AND status = 'pending';
        
        DECLARE @archived_count INT = @@ROWCOUNT;
        
        COMMIT TRANSACTION;
        
        SELECT 
            @deleted_count as deleted_count,
            @archived_count as archived_count,
            @cutoff_date as cutoff_date;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO

PRINT 'Stored procedure sp_cleanup_dlq_errors created successfully';
GO

-- =============================================
-- View for quick access to active errors
-- =============================================
IF EXISTS (SELECT * FROM sys.views WHERE name = 'vw_active_dlq_errors')
    DROP VIEW vw_active_dlq_errors;
GO

CREATE VIEW vw_active_dlq_errors AS
SELECT 
    e.id,
    e.message_id,
    e.sensor_id,
    e.sensor_type,
    e.error_type,
    e.error_category,
    e.error_message,
    e.dead_lettered_time,
    e.delivery_count,
    e.status,
    e.recovery_attempts,
    e.last_recovery_attempt,
    DATEDIFF(MINUTE, e.dead_lettered_time, GETUTCDATE()) as age_in_minutes,
    (SELECT COUNT(*) FROM dlq_recovery r WHERE r.dlq_error_id = e.id) as total_recovery_attempts,
    (SELECT TOP 1 recovery_status FROM dlq_recovery r WHERE r.dlq_error_id = e.id ORDER BY recovery_time DESC) as last_recovery_status
FROM dlq_errors e
WHERE e.status IN ('pending', 'failed')
    AND e.dead_lettered_time >= DATEADD(DAY, -30, GETUTCDATE());
GO

PRINT 'View vw_active_dlq_errors created successfully';
GO

-- =============================================
-- Verify table creation
-- =============================================
SELECT 
    'dlq_errors' as table_name,
    COUNT(*) as row_count
FROM dlq_errors
UNION ALL
SELECT 
    'dlq_recovery',
    COUNT(*)
FROM dlq_recovery
UNION ALL
SELECT 
    'dlq_statistics',
    COUNT(*)
FROM dlq_statistics
UNION ALL
SELECT 
    'dlq_alerts',
    COUNT(*)
FROM dlq_alerts;
GO

PRINT '';
PRINT '========================================';
PRINT 'DLQ Tables created successfully!';
PRINT '========================================';
PRINT 'Tables created:';
PRINT '  - dlq_errors';
PRINT '  - dlq_recovery';
PRINT '  - dlq_statistics';
PRINT '  - dlq_alerts';
PRINT '';
PRINT 'Stored Procedures created:';
PRINT '  - sp_get_dlq_statistics';
PRINT '  - sp_cleanup_dlq_errors';
PRINT '';
PRINT 'Views created:';
PRINT '  - vw_active_dlq_errors';
PRINT '========================================';
GO

