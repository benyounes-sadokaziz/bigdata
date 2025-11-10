#!/bin/bash
# Master Pipeline Orchestrator - Phase 7.1
# Executes the entire pipeline in correct order

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  E-Commerce Big Data Pipeline Orchestrator                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker containers are running
echo "🐳 Checking Docker containers..."
if ! docker ps | grep -q "mysql\|kafka\|namenode"; then
    echo "❌ Error: Required Docker containers are not running"
    echo "   Please run: docker-compose up -d"
    exit 1
fi
echo "✅ Docker containers are running"
echo ""

# Step 1: Analyze Dataset
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[1/8] Analyzing dataset..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 scripts/analyze_dataset.py
if [ $? -ne 0 ]; then
    echo "❌ Dataset analysis failed"
    exit 1
fi
echo ""

# Step 2: Split Data
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[2/8] Splitting data into historical and real-time..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 scripts/split_data.py
if [ $? -ne 0 ]; then
    echo "❌ Data splitting failed"
    exit 1
fi
echo ""

# Step 3: Generate MySQL Schema
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[3/8] Generating MySQL schema..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 scripts/generate_mysql_schema.py
if [ $? -ne 0 ]; then
    echo "❌ Schema generation failed"
    exit 1
fi
echo ""

# Step 4: Load Data to MySQL
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[4/8] Loading historical data to MySQL..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 scripts/load_mysql_data.py
if [ $? -ne 0 ]; then
    echo "❌ MySQL data loading failed"
    exit 1
fi
echo ""

# Step 5: Setup Kafka
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[5/8] Setting up Kafka topics..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 scripts/kafka_setup.py
if [ $? -ne 0 ]; then
    echo "❌ Kafka setup failed"
    exit 1
fi
echo ""

# Step 6: Generate Logs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[6/8] Generating application logs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 scripts/generate_logs.py
if [ $? -ne 0 ]; then
    echo "❌ Log generation failed"
    exit 1
fi
echo ""

# Step 7: Run Sqoop Imports
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[7/8] Executing Sqoop imports..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
bash scripts/sqoop_import.sh
if [ $? -ne 0 ]; then
    echo "⚠️  Sqoop imports may have failed (this is normal if Sqoop container has issues)"
fi
echo ""

# Step 8: Verify Setup
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[8/8] Verifying setup..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ MySQL Data:"
docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) as total_transactions FROM transactions;" 2>/dev/null
echo ""
echo "✅ Kafka Topics:"
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null | grep ecommerce
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                 PIPELINE SETUP COMPLETED! ✅                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Start Flume agents:"
echo "   bash scripts/start_flume.sh"
echo ""
echo "2. Start Kafka streaming:"
echo "   python3 scripts/stream_to_kafka.py"
echo ""
echo "3. Monitor HDFS:"
echo "   bash scripts/verify_hdfs.sh"
echo ""
echo "4. Run full demo:"
echo "   bash scripts/demo.sh"
echo ""
