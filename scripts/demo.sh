#!/bin/bash
# Demo Runner - Phase 7.4
# Runs a live demonstration of the entire system

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       E-Commerce Analytics Platform - LIVE DEMO           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Wait for user input
wait_for_user() {
    echo ""
    echo "Press Enter to continue..."
    read
}

# Demo Step 1: Show MySQL Data
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[DEMO 1] Historical Data in MySQL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Total transactions in MySQL:"
docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) as total_transactions FROM transactions;"
echo ""
echo "📊 Revenue by category:"
docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT product_category, SUM(total_revenue) as total_revenue FROM transactions GROUP BY product_category ORDER BY total_revenue DESC LIMIT 5;"
echo ""
echo "📊 Sample transactions:"
docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT * FROM transactions LIMIT 5;"
wait_for_user

# Demo Step 2: Sqoop Import
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[DEMO 2] Sqoop: Importing MySQL → HDFS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔄 Running Sqoop import..."
bash scripts/sqoop_import.sh
echo ""
echo "📂 Files in HDFS after Sqoop import:"
docker exec namenode hdfs dfs -ls /user/sqoop/
wait_for_user

# Demo Step 3: Generate and Process Logs
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[DEMO 3] Flume: Log File Processing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Checking generated logs..."
ls -lh logs/incoming/ 2>/dev/null || echo "No logs found"
echo ""
echo "🚀 Starting Flume log agent..."
bash scripts/start_flume.sh
echo ""
echo "⏳ Waiting for Flume to process logs (30 seconds)..."
sleep 30
echo ""
echo "📂 Logs in HDFS:"
docker exec namenode hdfs dfs -ls -R /user/flume/logs/ 2>/dev/null || echo "No logs in HDFS yet"
wait_for_user

# Demo Step 4: Kafka Streaming
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[DEMO 4] Kafka: Real-time Transaction Stream"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Starting Kafka streaming (first 10 records with 1 sec delay)..."
echo ""
python3 scripts/stream_to_kafka.py shared-data/transactions_realtime.csv ecommerce-transactions --delay 1 &
STREAM_PID=$!

sleep 15

echo ""
echo "📨 Consuming messages from Kafka:"
python3 scripts/test_kafka_consumer.py --topic ecommerce-transactions --max 5

# Stop streaming
kill $STREAM_PID 2>/dev/null

wait_for_user

# Demo Step 5: Show Complete Data Lake
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[DEMO 5] Complete Data Lake in HDFS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
bash scripts/verify_hdfs.sh

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    DEMO COMPLETED! 🎉                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ MySQL: Historical data stored and queried"
echo "✅ Sqoop: Data imported from MySQL to HDFS"
echo "✅ Flume: Log files processed and stored in HDFS"
echo "✅ Kafka: Real-time transactions streamed"
echo "✅ HDFS: Complete data lake with all three data sources"
echo ""
echo "🌐 Access Points:"
echo "  • Hadoop UI: http://localhost:9870"
echo "  • MySQL: docker exec -it mysql mysql -usqoop -psqoop123 testdb"
echo "  • HDFS Browse: docker exec namenode hdfs dfs -ls -R /user/"
echo ""
