#!/usr/bin/env python3
"""
MySQL Schema Generator - Phase 1.3
Auto-generates MySQL table creation script based on Online Sales Data CSV
"""

import pandas as pd
import os
from pathlib import Path

def infer_sql_type(dtype, column_name, sample_values):
    """Infer SQL data type from pandas dtype"""
    dtype_str = str(dtype)
    
    # Check for specific columns
    if 'id' in column_name.lower():
        return "VARCHAR(50)"
    elif 'date' in column_name.lower():
        return "DATE"
    elif 'timestamp' in column_name.lower():
        return "DATETIME"
    elif dtype_str.startswith('int'):
        return "INT"
    elif dtype_str.startswith('float'):
        # Check if it's a price/revenue column
        if 'price' in column_name.lower() or 'revenue' in column_name.lower() or 'amount' in column_name.lower():
            return "DECIMAL(12,2)"
        return "DECIMAL(15,2)"
    elif dtype_str == 'object':
        # Infer string length from sample data
        max_len = max([len(str(v)) for v in sample_values if pd.notna(v)], default=50)
        if max_len <= 50:
            return "VARCHAR(50)"
        elif max_len <= 100:
            return "VARCHAR(100)"
        elif max_len <= 255:
            return "VARCHAR(255)"
        else:
            return "TEXT"
    else:
        return "VARCHAR(255)"

def generate_mysql_schema():
    """Generate MySQL schema from the sales data CSV"""
    
    # Dataset path
    data_dir = Path("/shared-data") if os.path.exists("/shared-data") else Path("shared-data")
    csv_file = data_dir / "transactions_historical.csv"
    
    # Fallback to original if split not done yet
    if not csv_file.exists():
        csv_file = data_dir / "Online Sales Data.csv"
    
    output_file = Path("sql/create_tables.sql")
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          MySQL Schema Generator                            ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    if not csv_file.exists():
        print(f"❌ Error: File not found at {csv_file}")
        return
    
    # Read the dataset
    print(f"📖 Reading {csv_file.name}...")
    df = pd.read_csv(csv_file)
    print(f"✓ Loaded {len(df):,} records with {len(df.columns)} columns\n")
    
    # Start building SQL
    sql_content = []
    sql_content.append("-- E-Commerce Database Schema")
    sql_content.append("-- Auto-generated from Online Sales Data")
    sql_content.append("-- Generated for MySQL 8.0+\n")
    sql_content.append("-- Drop database if exists and create fresh")
    sql_content.append("DROP DATABASE IF EXISTS testdb;")
    sql_content.append("CREATE DATABASE testdb;")
    sql_content.append("USE testdb;\n")
    
    # Generate transactions table
    sql_content.append("-- ============================================")
    sql_content.append("-- TRANSACTIONS TABLE")
    sql_content.append("-- ============================================\n")
    sql_content.append("DROP TABLE IF EXISTS transactions;")
    sql_content.append("CREATE TABLE transactions (")
    
    columns = []
    for col in df.columns:
        col_clean = col.replace(' ', '_').replace('-', '_').lower()
        sample_values = df[col].head(100).tolist()
        sql_type = infer_sql_type(df[col].dtype, col_clean, sample_values)
        
        # Primary key
        if col_clean == 'transaction_id':
            columns.append(f"    {col_clean} {sql_type} PRIMARY KEY")
        else:
            columns.append(f"    {col_clean} {sql_type}")
    
    sql_content.append(",\n".join(columns))
    sql_content.append(");\n")
    
    # Add indexes
    sql_content.append("-- Indexes for better query performance")
    sql_content.append("CREATE INDEX idx_date ON transactions(date);")
    sql_content.append("CREATE INDEX idx_category ON transactions(product_category);")
    sql_content.append("CREATE INDEX idx_region ON transactions(region);")
    sql_content.append("CREATE INDEX idx_payment ON transactions(payment_method);\n")
    
    # Create aggregated views
    sql_content.append("-- ============================================")
    sql_content.append("-- ANALYTICAL VIEWS")
    sql_content.append("-- ============================================\n")
    
    sql_content.append("-- Daily Sales Summary")
    sql_content.append("CREATE OR REPLACE VIEW daily_sales AS")
    sql_content.append("SELECT ")
    sql_content.append("    date,")
    sql_content.append("    COUNT(*) as transaction_count,")
    sql_content.append("    SUM(units_sold) as total_units,")
    sql_content.append("    SUM(total_revenue) as total_revenue,")
    sql_content.append("    AVG(total_revenue) as avg_transaction_value")
    sql_content.append("FROM transactions")
    sql_content.append("GROUP BY date")
    sql_content.append("ORDER BY date;\n")
    
    sql_content.append("-- Category Performance")
    sql_content.append("CREATE OR REPLACE VIEW category_performance AS")
    sql_content.append("SELECT ")
    sql_content.append("    product_category,")
    sql_content.append("    COUNT(*) as transaction_count,")
    sql_content.append("    SUM(units_sold) as total_units,")
    sql_content.append("    SUM(total_revenue) as total_revenue,")
    sql_content.append("    AVG(unit_price) as avg_price")
    sql_content.append("FROM transactions")
    sql_content.append("GROUP BY product_category")
    sql_content.append("ORDER BY total_revenue DESC;\n")
    
    sql_content.append("-- Regional Sales")
    sql_content.append("CREATE OR REPLACE VIEW regional_sales AS")
    sql_content.append("SELECT ")
    sql_content.append("    region,")
    sql_content.append("    COUNT(*) as transaction_count,")
    sql_content.append("    SUM(total_revenue) as total_revenue,")
    sql_content.append("    AVG(total_revenue) as avg_transaction_value")
    sql_content.append("FROM transactions")
    sql_content.append("GROUP BY region")
    sql_content.append("ORDER BY total_revenue DESC;\n")
    
    # Write to file
    sql_script = "\n".join(sql_content)
    
    print(f"{'='*60}")
    print("GENERATED SQL SCHEMA")
    print('='*60)
    print(sql_script)
    print(f"\n{'='*60}")
    
    print(f"\n💾 Saving schema to {output_file}...")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(sql_script)
    
    print(f"✓ Schema saved successfully!")
    print(f"\n✅ MySQL schema generation completed!\n")
    print("Next steps:")
    print("  1. Review the generated SQL file: sql/create_tables.sql")
    print("  2. Run load_mysql_data.py to populate the database")

if __name__ == "__main__":
    generate_mysql_schema()
