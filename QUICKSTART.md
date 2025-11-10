# 🚀 Quick Start Guide - E-Commerce Big Data Platform

## Complete Step-by-Step Execution Guide

### Prerequisites Check ✅
```bash
# Open WSL terminal
wsl

# Navigate to project
cd ~/bigdata-project  # or /mnt/c/Users/sadok/bigdata-project

# Verify Docker is running
docker ps

# Start all containers if not running
docker-compose up -d

# Wait for containers to be ready (30 seconds)
sleep 30
```

### Step 1: Install Python Dependencies 📦
```bash
# Install required packages
pip3 install --user pandas kafka-python mysql-connector-python pymysql sqlalchemy

# Verify installation
python3 -c "import pandas, kafka, mysql.connector; print('All packages installed!')"
```

### Step 2: Make Scripts Executable 🔧
```bash
chmod +x scripts/*.sh
```

### Step 3: Run the Complete Pipeline 🎯
```bash
# This runs ALL setup steps automatically
bash scripts/run_pipeline.sh
```

**What this does:**
1. ✅ Analyzes your Online Sales Data.csv
2. ✅ Splits data into historical (70%) and real-time (30%)
3. ✅ Generates MySQL schema
4. ✅ Loads historical data to MySQL
5. ✅ Creates Kafka topics
6. ✅ Generates application logs
7. ✅ Runs Sqoop imports to HDFS

**Expected Output:**
- MySQL database populated with ~168 transactions
- Kafka topics created
- Log files generated in `logs/incoming/`
- Data imported to HDFS via Sqoop

### Step 4: Start Flume Agents 📡
```bash
# Start both Flume agents (log processor and Kafka consumer)
bash scripts/start_flume.sh
```

**Wait 10-15 seconds for Flume to start processing...**

### Step 5: Start Kafka Streaming 📊
```bash
# Open a NEW terminal window/tab in WSL
wsl
cd ~/bigdata-project

# Stream transactions to Kafka (slow simulation - 2 sec delay)
python3 scripts/stream_to_kafka.py shared-data/transactions_realtime.csv ecommerce-transactions --delay 2
```

**This will stream ~72 transactions to Kafka in real-time!**

### Step 6: Monitor Everything 👀

**Option A: Real-time Monitor Dashboard**
```bash
# Open ANOTHER terminal
wsl
cd ~/bigdata-project

python3 scripts/monitor.py
```

**Option B: Manual Verification**
```bash
# Verify HDFS data
bash scripts/verify_hdfs.sh
```

**Option C: Test Kafka Consumer**
```bash
# See live Kafka messages
python3 scripts/test_kafka_consumer.py --topic ecommerce-transactions --max 10
```

### Step 7: Verify Complete Data Lake 🎉
```bash
# Check all data in HDFS
docker exec namenode hdfs dfs -ls -R /user/

# Should show:
# /user/sqoop/transactions           (MySQL data via Sqoop)
# /user/sqoop/high_value_transactions
# /user/flume/logs/                  (Application logs)
# /user/flume/kafka-transactions/    (Kafka streamed data)
```

---

## 🎬 Alternative: Run Interactive Demo

```bash
# This runs everything step-by-step with explanations
bash scripts/demo.sh
```

Press Enter at each step to see:
1. MySQL data querying
2. Sqoop import in action
3. Flume processing logs
4. Kafka streaming live
5. Complete HDFS data lake

---

## 🔍 Verification Commands

### Check MySQL Data
```bash
docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) as total FROM transactions;"
docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT * FROM transactions LIMIT 5;"
```

### Check Kafka Topics
```bash
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Check HDFS Data
```bash
# List all directories
docker exec namenode hdfs dfs -ls -R /user/

# View Sqoop data
docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 | head -5

# View Kafka data
docker exec namenode bash -c "hdfs dfs -cat '/user/flume/kafka-transactions/*/*/*/*/*.json' | head -1"

# View logs
docker exec namenode bash -c "hdfs dfs -cat '/user/flume/logs/*/*/*/*.log' | head -5"
```

### Check Flume Status
```bash
# View log agent logs
docker exec flume tail -n 50 /opt/flume/logs/log-agent.log

# View kafka agent logs
docker exec flume tail -n 50 /opt/flume/logs/kafka-agent.log
```

---

## 🌐 Access Web UIs

- **Hadoop NameNode UI**: http://localhost:9870
- **MySQL**: `docker exec -it mysql mysql -usqoop -psqoop123 testdb`

---

## 🛑 Stop Everything

```bash
# Stop Kafka streaming (Ctrl+C in streaming terminal)

# Stop Flume agents
docker exec flume pkill -f flume-ng

# Stop monitor (Ctrl+C in monitor terminal)

# Stop all containers
docker-compose down

# Or stop but keep data
docker-compose stop
```

---

## 📊 Expected Results

After complete execution:

| Component | Data Count | Location |
|-----------|------------|----------|
| MySQL | ~168 records | testdb.transactions |
| Kafka | ~72 messages | ecommerce-transactions topic |
| Sqoop (HDFS) | ~168 records | /user/sqoop/transactions |
| Flume Logs (HDFS) | ~5,000 lines | /user/flume/logs/ |
| Kafka Stream (HDFS) | ~72 records | /user/flume/kafka-transactions/ |

**Total Data in HDFS**: 3 sources (Sqoop, Flume logs, Kafka streams) ✅

---

## ⚠️ Troubleshooting

### Issue: "MySQL connection failed"
```bash
# Wait for MySQL to be ready
docker logs mysql
# Wait 30 seconds and retry
```

### Issue: "Kafka not ready"
```bash
# Check Kafka logs
docker logs kafka
# Restart Kafka
docker-compose restart kafka zookeeper
```

### Issue: "Sqoop import fails"
```bash
# Check if Sqoop container has MySQL connector
docker exec sqoop ls $SQOOP_HOME/lib/ | grep mysql
```

### Issue: "Flume not processing"
```bash
# Check Flume logs
docker logs flume
# Restart Flume
docker-compose restart flume
```

### Issue: "Python packages not found"
```bash
# Install in user directory
pip3 install --user pandas kafka-python mysql-connector-python
```

---

## 🎓 For Presentation

1. **Show Architecture**: Open PRESENTATION_OUTLINE.md
2. **Run Demo**: `bash scripts/demo.sh`
3. **Show Hadoop UI**: http://localhost:9870
4. **Show Live Data**: `bash scripts/verify_hdfs.sh`
5. **Explain Data Flow**:
   - Historical → MySQL → Sqoop → HDFS
   - Real-time → Kafka → Flume → HDFS
   - Logs → Files → Flume → HDFS

**Total Time**: ~10 minutes for complete pipeline execution

---

## 📝 Summary

```
CSV Data (240 records)
    ├─ 70% (168) → MySQL → Sqoop → HDFS ✅
    └─ 30% (72) → Kafka → Flume → HDFS ✅

Generated Logs (5000 lines)
    └─ Files → Flume → HDFS ✅

Result: Complete Big Data pipeline with 3 ingestion methods! 🎉
```
