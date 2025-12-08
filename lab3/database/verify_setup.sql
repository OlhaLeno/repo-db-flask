-- Script to verify database setup
-- Execute in iot-sensors-db database

-- Check user
SELECT name, type_desc, is_fixed_role 
FROM sys.database_principals 
WHERE name = 'CloudSAa321694e';

-- Check table
SELECT TABLE_NAME, TABLE_TYPE 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_NAME = 'sensor_data';

-- Check indexes
SELECT name, type_desc 
FROM sys.indexes 
WHERE object_id = OBJECT_ID('sensor_data');

-- Check user permissions
SELECT 
    dp.name AS principal_name,
    dp.type_desc AS principal_type,
    r.name AS role_name
FROM sys.database_role_members rm
INNER JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
INNER JOIN sys.database_principals dp ON rm.member_principal_id = dp.principal_id
WHERE dp.name = 'CloudSAa321694e';

