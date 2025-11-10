-- E-Commerce Database Schema
-- Auto-generated from Online Sales Data
-- Generated for MySQL 8.0+

-- Drop database if exists and create fresh
DROP DATABASE IF EXISTS testdb;
CREATE DATABASE testdb;
USE testdb;

-- ============================================
-- TRANSACTIONS TABLE
-- ============================================

DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    date DATE,
    product_category VARCHAR(50),
    product_name VARCHAR(50),
    units_sold INT,
    unit_price DECIMAL(12,2),
    total_revenue DECIMAL(12,2),
    region VARCHAR(50),
    payment_method VARCHAR(50)
);

-- Indexes for better query performance
CREATE INDEX idx_date ON transactions(date);
CREATE INDEX idx_category ON transactions(product_category);
CREATE INDEX idx_region ON transactions(region);
CREATE INDEX idx_payment ON transactions(payment_method);

-- ============================================
-- ANALYTICAL VIEWS
-- ============================================

-- Daily Sales Summary
CREATE OR REPLACE VIEW daily_sales AS
SELECT 
    date,
    COUNT(*) as transaction_count,
    SUM(units_sold) as total_units,
    SUM(total_revenue) as total_revenue,
    AVG(total_revenue) as avg_transaction_value
FROM transactions
GROUP BY date
ORDER BY date;

-- Category Performance
CREATE OR REPLACE VIEW category_performance AS
SELECT 
    product_category,
    COUNT(*) as transaction_count,
    SUM(units_sold) as total_units,
    SUM(total_revenue) as total_revenue,
    AVG(unit_price) as avg_price
FROM transactions
GROUP BY product_category
ORDER BY total_revenue DESC;

-- Regional Sales
CREATE OR REPLACE VIEW regional_sales AS
SELECT 
    region,
    COUNT(*) as transaction_count,
    SUM(total_revenue) as total_revenue,
    AVG(total_revenue) as avg_transaction_value
FROM transactions
GROUP BY region
ORDER BY total_revenue DESC;
