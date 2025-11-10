# E-Commerce Big Data Pipeline Scripts

## Overview
This directory contains all Python and Bash scripts for the Real-Time E-Commerce Analytics Platform using Kafka, Sqoop, and Flume.

## Prerequisites
Install Python dependencies:
```bash
pip3 install -r ../requirements.txt
```

Or inside WSL:
```bash
cd ~/bigdata-project
pip3 install --user pandas kafka-python mysql-connector-python
```

## Script Execution Order

### 1. Initial Setup (Run Once)
```bash
# Navigate to project directory
cd ~/bigdata-project

# Make all scripts executable
chmod +x scripts/*.sh

# Run the complete pipeline setup
bash scripts/run_pipeline.sh
```

This will execute all steps automatically:
- Analyze dataset
- Split data (70% historical, 30% real-time)
- Generate MySQL schema
- Load data to MySQL
- Setup Kafka topics
- Generate application logs
- Run Sqoop imports

### 2. Start Data Streaming

**Start Flume Agents:**
```bash
bash scripts/start_flume.sh
```

**Start Kafka Streaming:**
```bash
# Stream with 2-second delay between records
python3 scripts/stream_to_kafka.py

# Or with custom parameters
python3 scripts/stream_to_kafka.py shared-data/transactions_realtime.csv ecommerce-transactions --delay 1
```

### 3. Monitoring

**Verify HDFS Data:**
```bash
bash scripts/verify_hdfs.sh
```

**Real-time Monitoring:**
```bash
python3 scripts/monitor.py
```

**Test Kafka Consumer:**
```bash
python3 scripts/test_kafka_consumer.py --topic ecommerce-transactions --max 10
```

### 4. Run Full Demo
```bash
bash scripts/demo.sh
```

## Individual Script Usage

### Phase 1: Data Preparation

**analyze_dataset.py** - Analyze the sales dataset
```bash
python3 scripts/analyze_dataset.py
```

**split_data.py** - Split data into historical and real-time
```bash
python3 scripts/split_data.py
```

**generate_mysql_schema.py** - Generate SQL schema
```bash
python3 scripts/generate_mysql_schema.py
```

### Phase 2: MySQL Loading

**load_mysql_data.py** - Load data into MySQL
```bash
# Set environment variables if needed
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=sqoop
export MYSQL_PASSWORD=sqoop123

python3 scripts/load_mysql_data.py
```

### Phase 3: Kafka Operations

**kafka_setup.py** - Create Kafka topics
```bash
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
python3 scripts/kafka_setup.py
```

**stream_to_kafka.py** - Stream transactions to Kafka
```bash
# Basic usage
python3 scripts/stream_to_kafka.py

# With options
python3 scripts/stream_to_kafka.py shared-data/transactions_realtime.csv ecommerce-transactions --delay 2 --batch-size 5
```

**test_kafka_consumer.py** - Test Kafka consumer
```bash
# Consume 10 messages from beginning
python3 scripts/test_kafka_consumer.py --topic ecommerce-transactions --max 10

# Consume latest messages
python3 scripts/test_kafka_consumer.py --topic ecommerce-transactions --latest
```

### Phase 4: Log Generation

**generate_logs.py** - Generate application logs
```bash
# Basic usage
python3 scripts/generate_logs.py

# With custom parameters
python3 scripts/generate_logs.py shared-data/transactions_realtime.csv --output-dir logs/incoming --logs-per-file 2000 --num-files 10
```

### Phase 5: Sqoop Operations

**sqoop_import.sh** - Import from MySQL to HDFS
```bash
bash scripts/sqoop_import.sh
```

**sqoop_export.sh** - Export from HDFS to MySQL
```bash
bash scripts/sqoop_export.sh
```

### Phase 6 & 7: Flume & Orchestration

**start_flume.sh** - Start Flume agents
```bash
bash scripts/start_flume.sh
```

**verify_hdfs.sh** - Verify HDFS data
```bash
bash scripts/verify_hdfs.sh
```

**demo.sh** - Run live demonstration
```bash
bash scripts/demo.sh
```

### Phase 8: Monitoring

**monitor.py** - Real-time pipeline monitoring
```bash
python3 scripts/monitor.py
```

## Troubleshooting

### Docker Containers Not Running
```bash
# Check container status
docker ps

# Start all containers
docker-compose up -d

# Check logs
docker-compose logs -f
```

### MySQL Connection Issues
```bash
# Test MySQL connection
docker exec mysql mysql -usqoop -psqoop123 testdb -e "SHOW TABLES;"

# Check if MySQL is ready
docker exec mysql mysqladmin ping -h localhost
```

### Kafka Connection Issues
```bash
# List Kafka topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Check Kafka broker
docker logs kafka
```

### HDFS Issues
```bash
# Check Namenode status
docker exec namenode hdfs dfsadmin -report

# List HDFS directories
docker exec namenode hdfs dfs -ls -R /user/
```

### Python Package Issues
```bash
# Install packages inside Docker containers if needed
docker exec sqoop pip3 install pandas kafka-python mysql-connector-python
docker exec flume pip3 install pandas kafka-python
```

## Quick Commands Reference

```bash
# View MySQL data
docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) FROM transactions;"

# View Kafka messages
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic ecommerce-transactions --from-beginning --max-messages 5

# View HDFS files
docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 | head -10

# View Flume logs
docker exec flume tail -f /opt/flume/logs/log-agent.log

# Stop Flume agents
docker exec flume pkill -f flume-ng
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MYSQL_HOST` | localhost | MySQL hostname |
| `MYSQL_PORT` | 3306 | MySQL port |
| `MYSQL_USER` | sqoop | MySQL username |
| `MYSQL_PASSWORD` | sqoop123 | MySQL password |
| `KAFKA_BOOTSTRAP_SERVERS` | localhost:9092 | Kafka servers |

## Output Directories

- `shared-data/` - CSV files (original and split)
- `sql/` - Generated SQL schemas
- `logs/incoming/` - Generated application logs
- `/user/sqoop/` (HDFS) - Sqoop imported data
- `/user/flume/logs/` (HDFS) - Flume processed logs
- `/user/flume/kafka-transactions/` (HDFS) - Kafka streamed data

## Notes

- Scripts are designed to run both inside Docker containers and from the host machine
- All scripts include error handling and progress reporting
- Use WSL terminal for best compatibility on Windows
- Make sure Docker has enough resources (8GB RAM recommended)
