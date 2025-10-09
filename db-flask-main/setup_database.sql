USE bus;
-- Route table
CREATE TABLE IF NOT EXISTS route (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    start_point VARCHAR(255) NOT NULL,
    end_point VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
-- Stop table
CREATE TABLE IF NOT EXISTS stop (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
-- Driver table
CREATE TABLE IF NOT EXISTS driver (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    license_number VARCHAR(50) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
-- Bus table
CREATE TABLE IF NOT EXISTS bus (
    id INT AUTO_INCREMENT PRIMARY KEY,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    model VARCHAR(100),
    capacity INT,
    route_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES route(id) ON DELETE
    SET NULL
);
-- Route-Stop table
CREATE TABLE IF NOT EXISTS route_stop (
    id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    stop_id INT NOT NULL,
    price_from_previous DECIMAL(10, 2) DEFAULT 0.00,
    sequence_order INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (route_id) REFERENCES route(id) ON DELETE CASCADE,
    FOREIGN KEY (stop_id) REFERENCES stop(id) ON DELETE CASCADE,
    UNIQUE KEY unique_route_stop (route_id, stop_id)
);
-- Bus inspections table
CREATE TABLE IF NOT EXISTS bus_inspection (
    id INT AUTO_INCREMENT PRIMARY KEY,
    bus_id INT NOT NULL,
    inspection_date DATE NOT NULL,
    inspection_result ENUM('PASS', 'FAIL', 'CONDITIONAL') NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (bus_id) REFERENCES bus(id) ON DELETE CASCADE
);
-- Creating indexes to improve performance
CREATE INDEX idx_bus_route_id ON bus(route_id);
CREATE INDEX idx_route_stop_route_id ON route_stop(route_id);
CREATE INDEX idx_route_stop_stop_id ON route_stop(stop_id);
CREATE INDEX idx_bus_inspection_bus_id ON bus_inspection(bus_id);
CREATE INDEX idx_bus_inspection_date ON bus_inspection(inspection_date);
-- Inserting test data
INSERT INTO route (name, start_point, end_point)
VALUES ('Route 1', 'City center', 'Train station'),
    ('Route 2', 'Airport', 'City center'),
    ('Route 3', 'University', 'Shopping mall');
INSERT INTO stop (name, latitude, longitude)
VALUES ('Central Square', 50.4501, 30.5234),
    ('Train Station', 50.4408, 30.4895),
    ('Airport', 50.4019, 30.4495),
    ('University', 50.4501, 30.5234),
    ('Shopping Mall', 50.4501, 30.5234);
INSERT INTO driver (name, license_number, phone)
VALUES ('Ivan Petrenko', 'DL123456', '+380501234567'),
    ('Maria Kovalenko', 'DL789012', '+380507654321'),
    ('Olexiy Sydorenko', 'DL345678', '+380509876543');
INSERT INTO bus (license_plate, model, capacity, route_id)
VALUES ('AA1234BB', 'Mercedes Sprinter', 25, 1),
    ('CC5678DD', 'Volkswagen Crafter', 30, 1),
    ('EE9012FF', 'Ford Transit', 20, 2),
    ('GG3456HH', 'Iveco Daily', 35, 3);
INSERT INTO route_stop (
        route_id,
        stop_id,
        price_from_previous,
        sequence_order
    )
VALUES (1, 1, 0.00, 1),
    (1, 2, 15.50, 2),
    (2, 3, 0.00, 1),
    (2, 1, 25.00, 2),
    (3, 4, 0.00, 1),
    (3, 5, 12.00, 2);
INSERT INTO bus_inspection (
        bus_id,
        inspection_date,
        inspection_result,
        remarks
    )
VALUES (
        1,
        '2024-01-15',
        'PASS',
        'All systems are functioning normally'
    ),
    (
        2,
        '2024-01-20',
        'PASS',
        'Minor body damage'
    ),
    (3, '2024-01-25', 'FAIL', 'Brake repair needed'),
    (
        4,
        '2024-01-30',
        'PASS',
        'Technical condition is excellent'
    );
-- Checking the created tables
SHOW TABLES;
-- Checking data
SELECT 'Routes:' as table_name,
    COUNT(*) as count
FROM route
UNION ALL
SELECT 'Stops:',
    COUNT(*)
FROM stop
UNION ALL
SELECT 'Drivers:',
    COUNT(*)
FROM driver
UNION ALL
SELECT 'Buses:',
    COUNT(*)
FROM bus
UNION ALL
SELECT 'Route Stops:',
    COUNT(*)
FROM route_stop
UNION ALL
SELECT 'Inspections:',
    COUNT(*)
FROM bus_inspection;
SELECT 'Database setup completed successfully!' as status;