-- Create or reset password for login CloudSAa321694e
-- EXECUTE IN MASTER DATABASE!
-- Select "master" database in Query editor before execution

-- Drop login if exists (to recreate)
IF EXISTS (SELECT * FROM sys.sql_logins WHERE name = 'CloudSAa321694e')
BEGIN
    DROP LOGIN [CloudSAa321694e];
    PRINT 'Existing login CloudSAa321694e dropped';
END

-- Create login with new password
CREATE LOGIN [CloudSAa321694e] WITH PASSWORD = 'Olhalenyo189';
PRINT 'Login CloudSAa321694e created with password: Olhalenyo189';

-- Verify
SELECT name, type_desc, create_date 
FROM sys.sql_logins 
WHERE name = 'CloudSAa321694e';

