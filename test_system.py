#!/usr/bin/env python3
"""
Simple Test Script - Verifies each component step by step
"""

import subprocess
import time

def run_cmd(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

print("="*60)
print("COMPREHENSIVE SYSTEM CHECK")
print("="*60)
print()

# Test 1: Check data files
print("Test 1: Checking data files...")
import os
files = ['shared-data/Online Sales Data.csv', 
         'shared-data/transactions_historical.csv',
         'shared-data/transactions_realtime.csv']
for f in files:
    exists = os.path.exists(f)
    print(f"  {'✅' if exists else '❌'} {f}")
print()

# Test 2: Check MySQL
print("Test 2: Checking MySQL connection and data...")
success, out, err = run_cmd('docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) FROM transactions;" -s -N 2>/dev/null')
if success:
    count = out.strip()
    print(f"  ✅ MySQL connected - {count} transactions found")
else:
    print(f"  ❌ MySQL error: {err}")
print()

# Test 3: Check Kafka
print("Test 3: Checking Kafka topics...")
success, out, err = run_cmd('docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null')
if success and 'ecommerce' in out:
    topics = [t for t in out.split('\n') if 'ecommerce' in t]
    print(f"  ✅ Found {len(topics)} Kafka topics:")
    for t in topics:
        print(f"     - {t}")
else:
    print(f"  ❌ Kafka error or no topics found")
print()

# Test 4: Check HDFS
print("Test 4: Checking HDFS...")
success, out, err = run_cmd('docker exec namenode hdfs dfs -ls / 2>/dev/null')
if success:
    print(f"  ✅ HDFS accessible")
    # Create /user directory if it doesn't exist
    run_cmd('docker exec namenode hdfs dfs -mkdir -p /user/sqoop')
    run_cmd('docker exec namenode hdfs dfs -mkdir -p /user/flume')
    print(f"  ✅ Created /user directories")
else:
    print(f"  ❌ HDFS not accessible: {err}")
print()

# Test 5: Test Sqoop connection
print("Test 5: Testing Sqoop to MySQL connection...")
success, out, err = run_cmd('docker exec sqoop sqoop list-databases --connect jdbc:mysql://mysql:3306/ --username sqoop --password sqoop123 2>/dev/null')
if success and 'testdb' in out:
    print(f"  ✅ Sqoop can connect to MySQL")
else:
    print(f"  ❌ Sqoop connection failed")
    if err:
        print(f"     Error: {err[:200]}")
print()

# Test 6: Test Python packages
print("Test 6: Testing Python packages...")
packages = ['pandas', 'kafka', 'mysql.connector']
for pkg in packages:
    try:
        __import__(pkg)
        print(f"  ✅ {pkg}")
    except ImportError:
        print(f"  ❌ {pkg} not installed")
print()

# Test 7: Run a simple Sqoop import
print("Test 7: Attempting simple Sqoop import...")
print("  This may take 30 seconds...")
success, out, err = run_cmd("""
docker exec sqoop sqoop import \
    --connect jdbc:mysql://mysql:3306/testdb \
    --username sqoop \
    --password sqoop123 \
    --table transactions \
    --target-dir /user/sqoop/test_import \
    --delete-target-dir \
    --m 1 2>&1
""")
if success:
    print(f"  ✅ Sqoop import successful!")
    # Check if data is in HDFS
    success2, out2, _ = run_cmd('docker exec namenode hdfs dfs -ls /user/sqoop/test_import/')
    if success2:
        print(f"  ✅ Data visible in HDFS:")
        print("     " + out2.strip().replace('\n', '\n     '))
else:
    print(f"  ❌ Sqoop import failed")
    if "Error" in out or "Error" in err:
        print("     " + (out + err)[:500])
print()

print("="*60)
print("SYSTEM CHECK COMPLETE")
print("="*60)
print()
print("Next steps:")
print("  1. If all tests pass, run: python3 scripts/stream_to_kafka.py")
print("  2. Monitor with: python3 scripts/monitor.py")
print("  3. Verify HDFS: bash scripts/verify_hdfs.sh")
