-- Create sample database and tables for Sqoop testing

USE testdb;

-- Create employees table
CREATE TABLE IF NOT EXISTS employees (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    department VARCHAR(50),
    salary DECIMAL(10,2),
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO employees (first_name, last_name, email, department, salary, hire_date) VALUES
('John', 'Doe', 'john.doe@company.com', 'IT', 75000.00, '2020-01-15'),
('Jane', 'Smith', 'jane.smith@company.com', 'HR', 65000.00, '2019-03-22'),
('Mike', 'Johnson', 'mike.johnson@company.com', 'Finance', 80000.00, '2018-07-10'),
('Sarah', 'Williams', 'sarah.williams@company.com', 'IT', 72000.00, '2021-02-01'),
('Tom', 'Brown', 'tom.brown@company.com', 'Marketing', 68000.00, '2020-09-15'),
('Emily', 'Davis', 'emily.davis@company.com', 'IT', 77000.00, '2019-11-20'),
('Robert', 'Miller', 'robert.miller@company.com', 'Finance', 85000.00, '2017-05-12'),
('Lisa', 'Wilson', 'lisa.wilson@company.com', 'HR', 63000.00, '2021-08-03');

-- Create sales table
CREATE TABLE IF NOT EXISTS sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(100),
    quantity INT,
    price DECIMAL(10,2),
    sale_date DATE,
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample sales data
INSERT INTO sales (product_name, quantity, price, sale_date, region) VALUES
('Laptop', 5, 1200.00, '2024-01-15', 'North'),
('Mouse', 20, 25.00, '2024-01-16', 'South'),
('Keyboard', 15, 45.00, '2024-01-17', 'East'),
('Monitor', 8, 350.00, '2024-01-18', 'West'),
('Laptop', 3, 1200.00, '2024-01-19', 'North'),
('Headphones', 12, 75.00, '2024-01-20', 'South'),
('Webcam', 6, 95.00, '2024-01-21', 'East'),
('Mouse', 25, 25.00, '2024-01-22', 'West');

-- Create logs table for tracking
CREATE TABLE IF NOT EXISTS data_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    log_level VARCHAR(20),
    message TEXT,
    source VARCHAR(100),
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

GRANT ALL PRIVILEGES ON testdb.* TO 'sqoop'@'%';
FLUSH PRIVILEGES;
