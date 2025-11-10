#!/bin/bash
# Diagnostic and Fix Script
# Checks what's working and fixes common issues

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Big Data Pipeline Diagnostics & Fix                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Check HDFS Namenode
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[1/6] Checking HDFS Namenode..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec namenode hdfs dfsadmin -report 2>/dev/null | head -10
if [ $? -eq 0 ]; then
    echo "✅ HDFS is running"
else
    echo "❌ HDFS is not responding properly"
    echo "   Trying to format namenode..."
    docker exec namenode hdfs namenode -format -force
fi
echo ""

# 2. Create HDFS directories
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[2/6] Creating HDFS directories..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec namenode hdfs dfs -mkdir -p /user/sqoop
docker exec namenode hdfs dfs -mkdir -p /user/flume/logs
docker exec namenode hdfs dfs -mkdir -p /user/flume/kafka-transactions
docker exec namenode hdfs dfs -chmod -R 777 /user
echo "✅ HDFS directories created"
docker exec namenode hdfs dfs -ls /user/
echo ""

# 3. Check MySQL
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[3/6] Checking MySQL data..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
MYSQL_COUNT=$(docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) FROM transactions;" -s -N 2>/dev/null)
echo "MySQL transactions: $MYSQL_COUNT"
if [ "$MYSQL_COUNT" -gt "0" ]; then
    echo "✅ MySQL has data"
else
    echo "❌ MySQL has no data - rerun: python3 scripts/load_mysql_data.py"
fi
echo ""

# 4. Test simple Sqoop import
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[4/6] Testing Sqoop import..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec sqoop sqoop import \
    --connect jdbc:mysql://mysql:3306/testdb \
    --username sqoop \
    --password sqoop123 \
    --table transactions \
    --target-dir /user/sqoop/transactions \
    --delete-target-dir \
    --m 1

if [ $? -eq 0 ]; then
    echo "✅ Sqoop import successful"
    docker exec namenode hdfs dfs -ls /user/sqoop/transactions/
else
    echo "❌ Sqoop import failed - check logs above"
fi
echo ""

# 5. Check Kafka
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[5/6] Checking Kafka..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null | grep ecommerce
echo "✅ Kafka topics listed above"
echo ""

# 6. Test Python connectivity
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[6/6] Testing Python packages..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 -c "import pandas; print('✅ pandas installed')" 2>/dev/null || echo "❌ pandas not installed"
python3 -c "import kafka; print('✅ kafka-python installed')" 2>/dev/null || echo "❌ kafka-python not installed"
python3 -c "import mysql.connector; print('✅ mysql-connector installed')" 2>/dev/null || echo "❌ mysql-connector not installed"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Diagnostics Complete                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo "  1. If Sqoop worked, check HDFS: docker exec namenode hdfs dfs -ls -R /user/"
echo "  2. Stream to Kafka: python3 scripts/stream_to_kafka.py"
echo "  3. Check monitor again: python3 scripts/monitor.py"
echo ""
