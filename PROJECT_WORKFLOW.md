# Big Data Project Workflow - Real-Time E-Commerce Analytics Platform

## PROJECT OVERVIEW
We are building a Real-Time E-Commerce Analytics Platform using Kafka, Sqoop, and Flume to demonstrate a complete Big Data pipeline. The project analyzes customer behavior, product performance, and sales trends across a global marketplace.

---

## DATASET INFORMATION
- **Source**: Kaggle - Online Sales Dataset (Popular Marketplace Data)
- **Files Expected**: 
  - customers.csv (or similar user data)
  - products.csv (or similar product catalog)
  - transactions.csv (or similar sales data)
- **Location**: `/mnt/c/Users/sadok/bigdata-project/shared-data/`

---

## ARCHITECTURE OVERVIEW

```
Dataset Files (CSV)
    │
    ├──► MySQL Database (Historical Data)
    │       │
    │       └──► Sqoop Import ──► HDFS (/user/sqoop/)
    │
    ├──► Kafka Stream (Real-Time Transactions)
    │       │
    │       └──► Flume Consumer ──► HDFS (/user/flume/kafka-data/)
    │
    └──► Log Generator (Application Logs)
            │
            └──► Flume Spooling ──► HDFS (/user/flume/logs/)
```

---

## PHASE 1: DATA PREPARATION SCRIPTS

### Script 1.1: Dataset Analyzer (`analyze_dataset.py`)
**Purpose**: Analyze the downloaded Kaggle dataset to understand structure

**Requirements**:
```python
# Input: CSV files from Kaggle dataset
# Output: Report showing:
#   - File names and sizes
#   - Column names and types
#   - Row counts
#   - Sample data (first 5 rows)
#   - Recommended split strategy (70% historical, 30% real-time)

# Libraries: pandas, os
# Location: /bigdata-project/scripts/analyze_dataset.py
```

**Key Functions**:
1. List all CSV files in shared-data directory
2. Read each CSV and print schema
3. Identify transaction/time-based columns
4. Suggest which file to use for which component (MySQL/Kafka/Logs)

---

### Script 1.2: Data Splitter (`split_data.py`)
**Purpose**: Split dataset into historical (MySQL) and real-time (Kafka) portions

**Requirements**:
```python
# Input: 
#   - transactions.csv (or main sales file)
#   - Split ratio: 70-30 or by date threshold

# Output:
#   - transactions_historical.csv (70% - older data)
#   - transactions_realtime.csv (30% - newer data)
#   - customers_full.csv (all customers for MySQL)
#   - products_full.csv (all products for MySQL)

# Logic:
#   - If dataset has date column: split by date (older dates → historical)
#   - If no date: split by row count (first 70% → historical)
#   - Maintain referential integrity (customer/product IDs)

# Libraries: pandas
# Location: /bigdata-project/scripts/split_data.py
```

---

### Script 1.3: MySQL Schema Generator (`generate_mysql_schema.py`)
**Purpose**: Auto-generate MySQL table creation scripts based on CSV structure

**Requirements**:
```python
# Input: CSV files (customers, products, transactions)
# Output: SQL file with CREATE TABLE statements

# Logic:
#   - Read CSV headers
#   - Infer data types (int, varchar, decimal, date)
#   - Generate CREATE TABLE with appropriate types
#   - Add primary keys and indexes
#   - Generate LOAD DATA INFILE statements

# Output File: /bigdata-project/sql/create_tables.sql

# Example Output:
"""
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255),
    email VARCHAR(255),
    country VARCHAR(100),
    registration_date DATE
);

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10,2),
    stock INT
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    quantity INT,
    total_amount DECIMAL(10,2),
    transaction_date DATETIME,
    payment_method VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
"""

# Libraries: pandas, sqlalchemy (optional)
# Location: /bigdata-project/scripts/generate_mysql_schema.py
```

---

## PHASE 2: MYSQL DATA LOADING

### Script 2.1: MySQL Data Loader (`load_mysql_data.py`)
**Purpose**: Load historical data into MySQL database

**Requirements**:
```python
# Input:
#   - transactions_historical.csv
#   - customers_full.csv
#   - products_full.csv

# Output: Data loaded into MySQL tables in 'testdb' database

# Process:
#   1. Connect to MySQL (host='mysql' or 'localhost', user='sqoop', password='sqoop123')
#   2. Create database 'testdb' if not exists
#   3. Execute schema SQL from Phase 1
#   4. Load CSV files into respective tables using pandas.to_sql() or LOAD DATA
#   5. Verify row counts
#   6. Print success message with statistics

# Connection Details:
#   - Host: localhost (or mysql for Docker)
#   - Port: 3306
#   - User: sqoop
#   - Password: sqoop123
#   - Database: testdb

# Libraries: pandas, mysql-connector-python or pymysql
# Location: /bigdata-project/scripts/load_mysql_data.py
```

**Error Handling**:
- Check if MySQL is running
- Handle duplicate keys
- Validate foreign key constraints
- Rollback on errors

---

## PHASE 3: KAFKA STREAMING SIMULATOR

### Script 3.1: Kafka Topic Manager (`kafka_setup.py`)
**Purpose**: Create and configure Kafka topics

**Requirements**:
```python
# Input: Topic configurations
# Output: Created Kafka topics

# Topics to Create:
#   1. 'ecommerce-transactions' (main transaction stream)
#   2. 'ecommerce-customers' (customer updates)
#   3. 'ecommerce-products' (product updates)

# Configuration:
#   - Bootstrap servers: 'kafka:29092' (inside Docker) or 'localhost:9092' (outside)
#   - Partitions: 3
#   - Replication factor: 1

# Functions:
#   - create_topic(topic_name, partitions=3, replication=1)
#   - list_topics()
#   - delete_topic(topic_name) [optional, for cleanup]

# Libraries: kafka-python
# Location: /bigdata-project/scripts/kafka_setup.py
```

---

### Script 3.2: Real-Time Transaction Streamer (`stream_to_kafka.py`)
**Purpose**: Simulate real-time transactions by streaming CSV data to Kafka

**Requirements**:
```python
# Input: transactions_realtime.csv
# Output: Records streamed to Kafka topic 'ecommerce-transactions'

# Features:
#   1. Read CSV file row by row
#   2. Add real-time metadata:
#      - streaming_timestamp (current time)
#      - record_number (sequential ID)
#      - event_type: "NEW_ORDER", "PAYMENT_CONFIRMED", etc.
#   3. Serialize to JSON
#   4. Send to Kafka with configurable delay (default: 1-2 seconds per record)
#   5. Print progress: "Sent record X/Y to Kafka"
#   6. Handle KeyboardInterrupt gracefully

# Kafka Configuration:
#   - Bootstrap servers: 'kafka:29092'
#   - Topic: 'ecommerce-transactions'
#   - Value serializer: JSON

# Command Line Arguments:
#   - csv_file: path to transactions_realtime.csv
#   - topic: Kafka topic name (default: 'ecommerce-transactions')
#   - delay: seconds between records (default: 2)
#   - batch_size: records to send before sleeping (default: 1)

# Example Usage:
#   python3 stream_to_kafka.py transactions_realtime.csv ecommerce-transactions --delay 1

# Libraries: kafka-python, pandas, json, time
# Location: /bigdata-project/scripts/stream_to_kafka.py
```

---

### Script 3.3: Kafka Consumer Tester (`test_kafka_consumer.py`)
**Purpose**: Test Kafka streaming by consuming and displaying messages

**Requirements**:
```python
# Input: Kafka topic name
# Output: Print consumed messages to console

# Features:
#   - Consume from beginning or latest
#   - Pretty print JSON messages
#   - Count total messages received
#   - Auto-stop after N messages or timeout

# Libraries: kafka-python, json
# Location: /bigdata-project/scripts/test_kafka_consumer.py
```

---

## PHASE 4: LOG FILE GENERATION

### Script 4.1: Application Log Generator (`generate_logs.py`)
**Purpose**: Generate realistic application logs from transaction data

**Requirements**:
```python
# Input: transactions_realtime.csv (or full dataset)
# Output: Log files in /logs/incoming/ directory

# Log Format:
"""
2024-11-10 15:30:45.123 [INFO] [TransactionService] Processing order #TXN12345
2024-11-10 15:30:45.234 [INFO] [PaymentService] Payment authorized for customer #CUST789: $129.99
2024-11-10 15:30:45.456 [INFO] [InventoryService] Stock updated for product #PROD456: -2 units
2024-11-10 15:30:46.789 [INFO] [NotificationService] Order confirmation sent to customer@email.com
2024-11-10 15:30:47.012 [WARN] [InventoryService] Low stock alert for product #PROD456: 3 units remaining
2024-11-10 15:30:48.234 [ERROR] [PaymentService] Payment declined for customer #CUST123: Insufficient funds
"""

# Log Components:
#   - Timestamp (microseconds)
#   - Log Level: INFO (70%), WARN (20%), ERROR (10%)
#   - Service Name: TransactionService, PaymentService, InventoryService, NotificationService
#   - Message: Based on transaction data
#   - Include: transaction_id, customer_id, product_id, amount, status

# Features:
#   - Generate multiple log files (simulate log rotation)
#   - File naming: ecommerce_app_YYYYMMDD_HHMMSS.log
#   - Configurable: logs per file, total files
#   - Random log levels and service names
#   - Include errors and warnings realistically

# Output Directory: /logs/incoming/

# Command Line Arguments:
#   - csv_file: source data
#   - output_dir: log directory (default: /logs/incoming)
#   - logs_per_file: entries per file (default: 1000)
#   - num_files: total files to generate (default: 5)

# Libraries: pandas, datetime, random
# Location: /bigdata-project/scripts/generate_logs.py
```

---

## PHASE 5: SQOOP OPERATIONS

### Script 5.1: Sqoop Import Helper (`sqoop_import.sh`)
**Purpose**: Bash script to execute Sqoop imports with proper parameters

**Requirements**:
```bash
#!/bin/bash
# Sqoop import commands for all tables

# MySQL Connection Info
MYSQL_HOST="mysql"
MYSQL_PORT="3306"
MYSQL_DB="testdb"
MYSQL_USER="sqoop"
MYSQL_PASSWORD="sqoop123"

# Function: Import full table
import_full_table() {
    TABLE_NAME=$1
    echo "Importing table: $TABLE_NAME"
    
    docker exec sqoop sqoop import \
        --connect jdbc:mysql://${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB} \
        --username ${MYSQL_USER} \
        --password ${MYSQL_PASSWORD} \
        --table ${TABLE_NAME} \
        --target-dir /user/sqoop/${TABLE_NAME} \
        --delete-target-dir \
        --m 1
    
    echo "✓ Import completed for $TABLE_NAME"
}

# Function: Import with WHERE clause
import_with_filter() {
    TABLE_NAME=$1
    WHERE_CLAUSE=$2
    OUTPUT_DIR=$3
    
    echo "Importing filtered data from: $TABLE_NAME"
    
    docker exec sqoop sqoop import \
        --connect jdbc:mysql://${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB} \
        --username ${MYSQL_USER} \
        --password ${MYSQL_PASSWORD} \
        --table ${TABLE_NAME} \
        --where "${WHERE_CLAUSE}" \
        --target-dir /user/sqoop/${OUTPUT_DIR} \
        --delete-target-dir \
        --m 1
    
    echo "✓ Filtered import completed"
}

# Function: Incremental import
import_incremental() {
    TABLE_NAME=$1
    CHECK_COLUMN=$2
    LAST_VALUE=$3
    
    echo "Incremental import for: $TABLE_NAME"
    
    docker exec sqoop sqoop import \
        --connect jdbc:mysql://${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB} \
        --username ${MYSQL_USER} \
        --password ${MYSQL_PASSWORD} \
        --table ${TABLE_NAME} \
        --incremental append \
        --check-column ${CHECK_COLUMN} \
        --last-value ${LAST_VALUE} \
        --target-dir /user/sqoop/${TABLE_NAME} \
        --m 1
    
    echo "✓ Incremental import completed"
}

# Main execution
echo "=== Starting Sqoop Imports ==="

# Import all tables
import_full_table "customers"
import_full_table "products"
import_full_table "transactions"

# Import filtered data (example: high-value transactions)
import_with_filter "transactions" "total_amount > 100" "high_value_transactions"

# Import incremental (example: new transactions)
# import_incremental "transactions" "transaction_id" "1000"

echo "=== All Sqoop imports completed ==="

# Location: /bigdata-project/scripts/sqoop_import.sh
```

---

### Script 5.2: Sqoop Export Helper (`sqoop_export.sh`)
**Purpose**: Export processed data from HDFS back to MySQL

**Requirements**:
```bash
#!/bin/bash
# Sqoop export commands

# Export aggregated results back to MySQL
export_to_mysql() {
    SOURCE_DIR=$1
    TARGET_TABLE=$2
    
    echo "Exporting from HDFS: $SOURCE_DIR to MySQL table: $TARGET_TABLE"
    
    docker exec sqoop sqoop export \
        --connect jdbc:mysql://mysql:3306/testdb \
        --username sqoop \
        --password sqoop123 \
        --table ${TARGET_TABLE} \
        --export-dir ${SOURCE_DIR} \
        --input-fields-terminated-by ',' \
        --m 1
    
    echo "✓ Export completed"
}

# Location: /bigdata-project/scripts/sqoop_export.sh
```

---

## PHASE 6: FLUME CONFIGURATION

### Config 6.1: Flume Agent for Logs (`flume-logs.conf`)
**Purpose**: Flume configuration for log file processing

**Requirements**:
```properties
# Agent name: log-agent

# Source: Spooling Directory (monitors /logs/incoming/)
log-agent.sources = log-source
log-agent.sources.log-source.type = spooldir
log-agent.sources.log-source.spoolDir = /logs/incoming
log-agent.sources.log-source.fileHeader = true
log-agent.sources.log-source.deletePolicy = immediate
log-agent.sources.log-source.fileSuffix = .processed

# Channel: Memory Channel
log-agent.channels = memory-channel
log-agent.channels.memory-channel.type = memory
log-agent.channels.memory-channel.capacity = 10000
log-agent.channels.memory-channel.transactionCapacity = 1000

# Sink: HDFS Sink (partitioned by date)
log-agent.sinks = hdfs-sink
log-agent.sinks.hdfs-sink.type = hdfs
log-agent.sinks.hdfs-sink.hdfs.path = hdfs://namenode:9000/user/flume/logs/%Y/%m/%d
log-agent.sinks.hdfs-sink.hdfs.filePrefix = ecommerce-logs-
log-agent.sinks.hdfs-sink.hdfs.fileSuffix = .log
log-agent.sinks.hdfs-sink.hdfs.rollInterval = 300
log-agent.sinks.hdfs-sink.hdfs.rollSize = 0
log-agent.sinks.hdfs-sink.hdfs.rollCount = 0
log-agent.sinks.hdfs-sink.hdfs.fileType = DataStream
log-agent.sinks.hdfs-sink.hdfs.writeFormat = Text
log-agent.sinks.hdfs-sink.hdfs.useLocalTimeStamp = true

# Bind source and sink to channel
log-agent.sources.log-source.channels = memory-channel
log-agent.sinks.hdfs-sink.channel = memory-channel

# Location: /bigdata-project/flume-conf/flume-logs.conf
```

---

### Config 6.2: Flume Agent for Kafka (`flume-kafka.conf`)
**Purpose**: Flume configuration for consuming from Kafka

**Requirements**:
```properties
# Agent name: kafka-agent

# Source: Kafka Source
kafka-agent.sources = kafka-source
kafka-agent.sources.kafka-source.type = org.apache.flume.source.kafka.KafkaSource
kafka-agent.sources.kafka-source.kafka.bootstrap.servers = kafka:29092
kafka-agent.sources.kafka-source.kafka.topics = ecommerce-transactions
kafka-agent.sources.kafka-source.kafka.consumer.group.id = flume-consumer
kafka-agent.sources.kafka-source.batchSize = 100
kafka-agent.sources.kafka-source.batchDurationMillis = 2000

# Channel: File Channel (more reliable)
kafka-agent.channels = file-channel
kafka-agent.channels.file-channel.type = file
kafka-agent.channels.file-channel.checkpointDir = /opt/flume/checkpoint/kafka
kafka-agent.channels.file-channel.dataDirs = /opt/flume/data/kafka

# Sink: HDFS Sink
kafka-agent.sinks = hdfs-sink
kafka-agent.sinks.hdfs-sink.type = hdfs
kafka-agent.sinks.hdfs-sink.hdfs.path = hdfs://namenode:9000/user/flume/kafka-transactions/%Y/%m/%d/%H
kafka-agent.sinks.hdfs-sink.hdfs.filePrefix = kafka-txn-
kafka-agent.sinks.hdfs-sink.hdfs.fileSuffix = .json
kafka-agent.sinks.hdfs-sink.hdfs.rollInterval = 600
kafka-agent.sinks.hdfs-sink.hdfs.rollSize = 0
kafka-agent.sinks.hdfs-sink.hdfs.rollCount = 0
kafka-agent.sinks.hdfs-sink.hdfs.fileType = DataStream
kafka-agent.sinks.hdfs-sink.hdfs.writeFormat = Text
kafka-agent.sinks.hdfs-sink.hdfs.useLocalTimeStamp = true

# Bind
kafka-agent.sources.kafka-source.channels = file-channel
kafka-agent.sinks.hdfs-sink.channel = file-channel

# Location: /bigdata-project/flume-conf/flume-kafka.conf
```

---

## PHASE 7: ORCHESTRATION & TESTING

### Script 7.1: Master Orchestrator (`run_pipeline.sh`)
**Purpose**: Execute the entire pipeline in correct order

**Requirements**:
```bash
#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  E-Commerce Big Data Pipeline Orchestrator                ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Step 1: Analyze Dataset
echo -e "\n[1/7] Analyzing dataset..."
python3 scripts/analyze_dataset.py

# Step 2: Split Data
echo -e "\n[2/7] Splitting data into historical and real-time..."
python3 scripts/split_data.py

# Step 3: Generate MySQL Schema
echo -e "\n[3/7] Generating MySQL schema..."
python3 scripts/generate_mysql_schema.py

# Step 4: Load Data to MySQL
echo -e "\n[4/7] Loading historical data to MySQL..."
python3 scripts/load_mysql_data.py

# Step 5: Setup Kafka
echo -e "\n[5/7] Setting up Kafka topics..."
python3 scripts/kafka_setup.py

# Step 6: Run Sqoop Imports
echo -e "\n[6/7] Executing Sqoop imports..."
bash scripts/sqoop_import.sh

# Step 7: Generate Logs
echo -e "\n[7/7] Generating application logs..."
python3 scripts/generate_logs.py

echo -e "\n✓ Pipeline setup completed!"
echo -e "\nNext steps:"
echo "  1. Start Flume agents: bash scripts/start_flume.sh"
echo "  2. Start Kafka streaming: python3 scripts/stream_to_kafka.py"
echo "  3. Monitor in HDFS: docker exec namenode hdfs dfs -ls -R /user/"

# Location: /bigdata-project/scripts/run_pipeline.sh
```

---

### Script 7.2: Flume Starter (`start_flume.sh`)
**Purpose**: Start both Flume agents

**Requirements**:
```bash
#!/bin/bash

echo "Starting Flume agents..."

# Start log processing agent
echo "Starting log-agent..."
docker exec -d flume flume-ng agent \
    --conf /opt/flume/conf \
    --conf-file /opt/flume/conf/flume-logs.conf \
    --name log-agent \
    -Dflume.root.logger=INFO,console

sleep 5

# Start Kafka consumer agent
echo "Starting kafka-agent..."
docker exec -d flume flume-ng agent \
    --conf /opt/flume/conf \
    --conf-file /opt/flume/conf/flume-kafka.conf \
    --name kafka-agent \
    -Dflume.root.logger=INFO,console

echo "✓ Both Flume agents started"
echo "Check logs: docker exec flume tail -f /opt/flume/logs/*.log"

# Location: /bigdata-project/scripts/start_flume.sh
```

---

### Script 7.3: HDFS Verification (`verify_hdfs.sh`)
**Purpose**: Verify all data has been written to HDFS

**Requirements**:
```bash
#!/bin/bash

echo "=== HDFS Data Verification ==="
echo ""

# Check Sqoop imports
echo "[1] Checking Sqoop imports..."
docker exec namenode hdfs dfs -ls -R /user/sqoop/ | grep -v "^d"

# Check Flume logs
echo -e "\n[2] Checking Flume log files..."
docker exec namenode hdfs dfs -ls -R /user/flume/logs/ | grep -v "^d"

# Check Flume Kafka data
echo -e "\n[3] Checking Kafka stream data..."
docker exec namenode hdfs dfs -ls -R /user/flume/kafka-transactions/ | grep -v "^d"

# Count records
echo -e "\n[4] Counting records in HDFS..."
echo "Sqoop - Customers:"
docker exec namenode hdfs dfs -cat /user/sqoop/customers/part-m-00000 | wc -l

echo "Sqoop - Transactions:"
docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 | wc -l

echo "Flume - Log entries:"
docker exec namenode hdfs dfs -cat /user/flume/logs/*/*.log | wc -l

echo -e "\n✓ Verification complete"

# Location: /bigdata-project/scripts/verify_hdfs.sh
```

---

### Script 7.4: Demo Runner (`demo.sh`)
**Purpose**: Run a live demonstration of the entire system

**Requirements**:
```bash
#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║       E-Commerce Analytics Platform - LIVE DEMO           ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Demo Step 1: Show MySQL Data
echo -e "\n[DEMO 1] Historical data in MySQL..."
docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) as total_transactions FROM transactions;"
echo "Press Enter to continue..."
read

# Demo Step 2: Sqoop Import
echo -e "\n[DEMO 2] Importing MySQL data to HDFS with Sqoop..."
bash scripts/sqoop_import.sh
docker exec namenode hdfs dfs -ls /user/sqoop/
echo "Press Enter to continue..."
read

# Demo Step 3: Start Kafka Streaming
echo -e "\n[DEMO 3] Starting real-time transaction stream to Kafka..."
echo "(This will run in background, check Kafka UI at http://localhost:8080)"
docker exec -d kafka bash -c "cd /shared-data && python3 stream_to_kafka.py transactions_realtime.csv ecommerce-transactions 2"
echo "✓ Streaming started"
sleep 5
echo "Checking Kafka messages..."
docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic ecommerce-transactions --from-beginning --max-messages 5
echo "Press Enter to continue..."
read

# Demo Step 4: Show Flume Processing
echo -e "\n[DEMO 4] Flume processing logs and Kafka data..."
bash scripts/start_flume.sh
echo "Waiting for Flume to process data..."
sleep 30
docker exec namenode hdfs dfs -ls -R /user/flume/
echo "Press Enter to continue..."
read

# Demo Step 5: Final Verification
echo -e "\n[DEMO 5] Final HDFS data lake view..."
bash scripts/verify_hdfs.sh

echo -e "\n╔════════════════════════════════════════════════════════════╗"
echo "║                    DEMO COMPLETED                          ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Location: /bigdata-project/scripts/demo.sh
```

---

## PHASE 8: MONITORING & VISUALIZATION

### Script 8.1: Pipeline Monitor (`monitor.py`)
**Purpose**: Real-time monitoring dashboard for the pipeline

**Requirements**:
```python
# Create a simple monitoring script that checks:
#   1. Kafka topics and message counts
#   2. MySQL row counts
#   3. HDFS directory sizes
#   4. Flume agent status
#   5. Latest processing timestamps

# Output: Terminal-based dashboard or web interface (Flask)
# Refresh every 5 seconds

# Libraries: kafka-python, mysql-connector, subprocess, time
# Location: /bigdata-project/scripts/monitor.py
```

---

## PROJECT STRUCTURE

```
bigdata-project/
├── shared-data/                    # Kaggle dataset location
│   ├── [original_csvs]            # Original downloaded files
│   ├── transactions_historical.csv
│   ├── transactions_realtime.csv
│   ├── customers_full.csv
│   └── products_full.csv
├── scripts/                        # All Python/Bash scripts
│   ├── analyze_dataset.py
│   ├── split_data.py
│   ├── generate_mysql_schema.py
│   ├── load_mysql_data.py
│   ├── kafka_setup.py
│   ├── stream_to_kafka.py
│   ├── test_kafka_consumer.py
│   ├── generate_logs.py
│   ├── sqoop_import.sh
│   ├── sqoop_export.sh
│   ├── start_flume.sh
│   ├── verify_hdfs.sh
│   ├── run_pipeline.sh
│   ├── demo.sh
│   └── monitor.py
├── sql/                           # Generated SQL schemas
│   └── create_tables.sql
├── flume-conf/                    # Flume configurations
│   ├── flume-logs.conf
│   └── flume-kafka.conf
├── logs/                          # Log file storage
│   └── incoming/                  # Flume spooling directory
├── docker-compose.yml
├── hadoop.env
└── README.md
```

---

## EXECUTION ORDER

1. **Setup** (One-time):
   ```bash
   docker-compose up -d
   bash scripts/run_pipeline.sh
   ```

2. **Demo/Testing**:
   ```bash
   bash scripts/demo.sh
   ```

3. **Monitoring**:
   ```bash
   python3 scripts/monitor.py
   ```

---

## KEY REQUIREMENTS FOR CODE GENERATION

1. **Error Handling**: All scripts must handle connection failures gracefully
2. **Logging**: Print progress messages and errors clearly
3. **Configurability**: Use command-line arguments or config files
4. **Documentation**: Include docstrings and comments
5. **Docker Compatibility**: Scripts should work inside containers or from host
6. **Data Validation**: Check file existence, row counts, data types
7. **Idempotency**: Scripts should be re-runnable without breaking

---

## PYTHON DEPENDENCIES

Create a requirements.txt:
```
pandas>=1.5.0
kafka-python>=2.0.2
mysql-connector-python>=8.0.0
pymysql>=1.0.0
sqlalchemy>=2.0.0
```

---

## TESTING CHECKLIST

- [ ] Dataset analyzed successfully
- [ ] Data split into historical/realtime
- [ ] MySQL schema generated
- [ ] Data loaded to MySQL
- [ ] Kafka topics created
- [ ] Sqoop imports working
- [ ] Logs generated
- [ ] Flume agents running
- [ ] Kafka streaming working
- [ ] Data visible in HDFS
- [ ] All three tools demonstrated

---

## PRESENTATION POINTS

1. **Why Big Data?**
   - Volume: Millions of transactions
   - Velocity: Real-time streaming needed
   - Variety: Structured (DB) + Semi-structured (logs) + Streaming

2. **Architecture Levels**:
   - Ingestion: Kafka, Sqoop, Flume
   - Storage: HDFS
   - Processing: (Future: Spark/Hive)

3. **How It Works**:
   - Show live demo
   - Explain data flow
   - Show HDFS contents

---

END OF WORKFLOW DOCUMENT
