#!/bin/bash
# HDFS Verification Script - Phase 7.3
# Verifies all data has been written to HDFS

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          HDFS Data Verification                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Namenode is running
if ! docker ps | grep -q "namenode"; then
    echo "❌ Error: Namenode container is not running"
    exit 1
fi

# Check Sqoop imports
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[1] Checking Sqoop Imports in HDFS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec namenode hdfs dfs -ls -R /user/sqoop/ 2>/dev/null || echo "⚠️  No Sqoop data found (run sqoop_import.sh first)"
echo ""

# Check Flume logs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[2] Checking Flume Log Files in HDFS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec namenode hdfs dfs -ls -R /user/flume/logs/ 2>/dev/null || echo "⚠️  No log data found (start Flume log-agent first)"
echo ""

# Check Flume Kafka data
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[3] Checking Kafka Stream Data in HDFS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker exec namenode hdfs dfs -ls -R /user/flume/kafka-transactions/ 2>/dev/null || echo "⚠️  No Kafka data found (start streaming and Flume kafka-agent first)"
echo ""

# Count records
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[4] Record Counts"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Sqoop - Transactions
echo -n "Sqoop - Transactions: "
docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 2>/dev/null | wc -l || echo "0"

# Sqoop - High Value Transactions
echo -n "Sqoop - High Value Transactions: "
docker exec namenode hdfs dfs -cat /user/sqoop/high_value_transactions/part-m-00000 2>/dev/null | wc -l || echo "0"

# Flume - Log entries
echo -n "Flume - Log Entries: "
docker exec namenode hdfs dfs -cat '/user/flume/logs/*/*/*/*.log' 2>/dev/null | wc -l || echo "0"

# Flume - Kafka transactions
echo -n "Flume - Kafka Transactions: "
docker exec namenode hdfs dfs -cat '/user/flume/kafka-transactions/*/*/*/*/*.json' 2>/dev/null | wc -l || echo "0"

echo ""

# Show sample data
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[5] Sample Data from HDFS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "📊 Sample Sqoop Data (first 3 lines):"
docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 2>/dev/null | head -3 || echo "No data"

echo ""
echo "📊 Sample Log Data (first 3 lines):"
docker exec namenode bash -c "hdfs dfs -cat '/user/flume/logs/*/*/*/*.log' 2>/dev/null | head -3" || echo "No data"

echo ""
echo "📊 Sample Kafka Data (first 1 record):"
docker exec namenode bash -c "hdfs dfs -cat '/user/flume/kafka-transactions/*/*/*/*/*.json' 2>/dev/null | head -1" || echo "No data"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Verification Complete ✅                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
