-- Execute this script in iot-sensors-db database
-- Select iot-sensors-db database in Query editor before execution

-- Check and drop user if exists
IF EXISTS (SELECT * FROM sys.database_principals WHERE name = 'CloudSAa321694e' AND type = 'S')
BEGIN
    DROP USER [CloudSAa321694e];
    PRINT 'Existing user CloudSAa321694e dropped';
END

-- Create user
CREATE USER [CloudSAa321694e] FOR LOGIN [CloudSAa321694e];

-- Grant permissions (only if user is not dbo)
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'CloudSAa321694e' AND is_fixed_role = 1)
BEGIN
    -- Check if user is not already in role
    IF NOT EXISTS (SELECT * FROM sys.database_role_members rm
                   INNER JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
                   INNER JOIN sys.database_principals m ON rm.member_principal_id = m.principal_id
                   WHERE r.name = 'db_datareader' AND m.name = 'CloudSAa321694e')
    BEGIN
        ALTER ROLE db_datareader ADD MEMBER [CloudSAa321694e];
    END
    
    IF NOT EXISTS (SELECT * FROM sys.database_role_members rm
                   INNER JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
                   INNER JOIN sys.database_principals m ON rm.member_principal_id = m.principal_id
                   WHERE r.name = 'db_datawriter' AND m.name = 'CloudSAa321694e')
    BEGIN
        ALTER ROLE db_datawriter ADD MEMBER [CloudSAa321694e];
    END
END
ELSE
BEGIN
    PRINT 'User CloudSAa321694e is dbo - has all permissions';
END

PRINT 'User CloudSAa321694e setup completed!';

