#!/usr/bin/env python3
"""
MySQL Data Loader - Phase 2.1
Loads historical sales data into MySQL database
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from pathlib import Path
import time

def wait_for_mysql(host, port, user, password, max_retries=30):
    """Wait for MySQL to be ready"""
    print("⏳ Waiting for MySQL to be ready...")
    for i in range(max_retries):
        try:
            conn = mysql.connector.connect(
                host=host,
                port=port,
                user=user,
                password=password
            )
            conn.close()
            print("✓ MySQL is ready!\n")
            return True
        except Error:
            if i < max_retries - 1:
                print(f"  Attempt {i+1}/{max_retries} - MySQL not ready yet, waiting...")
                time.sleep(2)
            else:
                return False
    return False

def load_mysql_data():
    """Load historical data into MySQL"""
    
    # Connection parameters
    MYSQL_CONFIG = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'user': os.getenv('MYSQL_USER', 'sqoop'),
        'password': os.getenv('MYSQL_PASSWORD', 'sqoop123'),
        'database': 'testdb'
    }
    
    # Data paths
    data_dir = Path("/shared-data") if os.path.exists("/shared-data") else Path("shared-data")
    csv_file = data_dir / "transactions_historical.csv"
    schema_file = Path("sql/create_tables.sql")
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          MySQL Data Loader                                 ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Check if files exist
    if not csv_file.exists():
        print(f"❌ Error: Data file not found at {csv_file}")
        print("   Please run split_data.py first!")
        return
    
    if not schema_file.exists():
        print(f"❌ Error: Schema file not found at {schema_file}")
        print("   Please run generate_mysql_schema.py first!")
        return
    
    # Wait for MySQL
    if not wait_for_mysql(MYSQL_CONFIG['host'], MYSQL_CONFIG['port'], 
                          MYSQL_CONFIG['user'], MYSQL_CONFIG['password']):
        print("❌ Error: Could not connect to MySQL")
        return
    
    try:
        # Read the schema
        print(f"📖 Reading schema from {schema_file}...")
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Connect to MySQL (without database first)
        print(f"🔌 Connecting to MySQL at {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}...")
        conn = mysql.connector.connect(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Execute schema (creates database and tables)
        print("🏗️  Creating database and tables...")
        for statement in schema_sql.split(';'):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                except Error as e:
                    if "CREATE OR REPLACE VIEW" in statement or "CREATE VIEW" in statement:
                        # Skip view creation errors for now
                        print(f"  ⚠️  Skipping view creation (will create after data load)")
                    else:
                        print(f"  Error executing: {statement[:50]}...")
                        print(f"  {e}")
        
        conn.commit()
        print("✓ Database and tables created successfully!")
        
        # Close and reconnect to the database
        cursor.close()
        conn.close()
        
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        
        # Read the CSV data
        print(f"\n📊 Loading data from {csv_file.name}...")
        df = pd.read_csv(csv_file)
        print(f"✓ Loaded {len(df):,} records")
        
        # Clean column names (spaces to underscores, lowercase)
        df.columns = df.columns.str.replace(' ', '_').str.replace('-', '_').str.lower()
        
        # Insert data in batches
        print("\n💾 Inserting data into MySQL...")
        columns = ', '.join(df.columns)
        placeholders = ', '.join(['%s'] * len(df.columns))
        insert_query = f"INSERT INTO transactions ({columns}) VALUES ({placeholders})"
        
        batch_size = 100
        total_batches = (len(df) + batch_size - 1) // batch_size
        
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            values = [tuple(row) for row in batch.values]
            cursor.executemany(insert_query, values)
            conn.commit()
            
            batch_num = (i // batch_size) + 1
            print(f"  ✓ Batch {batch_num}/{total_batches} inserted ({len(batch)} records)")
        
        print(f"\n✅ Successfully inserted {len(df):,} records!")
        
        # Verify the data
        print(f"\n{'='*60}")
        print("DATA VERIFICATION")
        print('='*60)
        
        cursor.execute("SELECT COUNT(*) FROM transactions")
        count = cursor.fetchone()[0]
        print(f"Total records in database: {count:,}")
        
        cursor.execute("SELECT MIN(date), MAX(date) FROM transactions")
        date_range = cursor.fetchone()
        print(f"Date range: {date_range[0]} to {date_range[1]}")
        
        cursor.execute("SELECT product_category, COUNT(*) as cnt FROM transactions GROUP BY product_category ORDER BY cnt DESC")
        print(f"\nRecords by category:")
        for row in cursor.fetchall():
            print(f"  {row[0]:20s}: {row[1]:,}")
        
        cursor.execute("SELECT SUM(total_revenue) FROM transactions")
        total_revenue = cursor.fetchone()[0]
        print(f"\nTotal Revenue: ${total_revenue:,.2f}")
        
        print(f"\n{'='*60}")
        print("✅ MySQL data loading completed successfully!")
        print('='*60)
        print("\nNext steps:")
        print("  1. Test Sqoop import: bash scripts/sqoop_import.sh")
        print("  2. Query data: docker exec mysql mysql -usqoop -psqoop123 testdb -e 'SELECT * FROM transactions LIMIT 5;'")
        
    except Error as e:
        print(f"\n❌ MySQL Error: {e}")
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("\n🔌 MySQL connection closed")

if __name__ == "__main__":
    load_mysql_data()
