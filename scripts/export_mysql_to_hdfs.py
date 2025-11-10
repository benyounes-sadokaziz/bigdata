#!/usr/bin/env python3
"""
MySQL to HDFS Data Export Script
Replaces Sqoop for simple data transfer
"""

import mysql.connector
import csv
import subprocess
import sys
from io import StringIO

def export_mysql_to_hdfs():
    print("=" * 60)
    print("MySQL to HDFS Export (Sqoop Alternative)")
    print("=" * 60)
    
    # Step 1: Connect to MySQL and fetch data
    print("\n[1/4] Connecting to MySQL...")
    try:
        conn = mysql.connector.connect(
            host='mysql',
            user='sqoop',
            password='sqoop123',
            database='testdb'
        )
        cursor = conn.cursor()
        
        print("✓ Connected successfully")
        
        # Step 2: Export data to CSV
        print("\n[2/4] Exporting data from MySQL...")
        cursor.execute("SELECT * FROM transactions")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        print(f"✓ Fetched {len(rows)} records")
        
        # Create CSV content
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow(columns)
        writer.writerows(rows)
        csv_content = csv_buffer.getvalue()
        
        # Write to local file
        local_file = '/tmp/transactions_export.csv'
        with open(local_file, 'w') as f:
            f.write(csv_content)
        
        print(f"✓ Saved to {local_file}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"✗ MySQL error: {e}")
        return False
    
    # Step 3: Upload to HDFS
    print("\n[3/4] Uploading to HDFS...")
    try:
        # Create directory
        subprocess.run([
            'hdfs', 'dfs', '-mkdir', '-p', '/user/sqoop/transactions'
        ], check=False)
        
        # Upload file
        result = subprocess.run([
            'hdfs', 'dfs', '-put', '-f', local_file,
            '/user/sqoop/transactions/part-m-00000.csv'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Successfully uploaded to HDFS")
        else:
            print(f"✗ HDFS upload failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ HDFS error: {e}")
        return False
    
    # Step 4: Verify
    print("\n[4/4] Verifying HDFS contents...")
    try:
        result = subprocess.run([
            'hdfs', 'dfs', '-ls', '/user/sqoop/transactions/'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout)
            print("✓ Verification complete")
            
            # Show sample
            print("\n" + "=" * 60)
            print("Sample Data (first 5 rows):")
            print("=" * 60)
            result = subprocess.run([
                'hdfs', 'dfs', '-cat', '/user/sqoop/transactions/part-m-00000.csv'
            ], capture_output=True, text=True)
            
            lines = result.stdout.split('\n')[:6]
            for line in lines:
                print(line)
                
            return True
        else:
            print(f"✗ Verification failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Verification error: {e}")
        return False

if __name__ == '__main__':
    success = export_mysql_to_hdfs()
    sys.exit(0 if success else 1)
