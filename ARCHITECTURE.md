# Big Data E-Commerce Analytics Platform - Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Components](#components)
4. [Data Flow](#data-flow)
5. [Docker Infrastructure](#docker-infrastructure)
6. [Deployment Guide](#deployment-guide)
7. [Monitoring & Visualization](#monitoring--visualization)

---

## Overview

This project implements a comprehensive **Big Data Analytics Platform** for e-commerce transaction processing, demonstrating real-time streaming, batch processing, and log aggregation using industry-standard tools.

### Key Technologies
- **Apache Kafka** - Real-time event streaming
- **Apache Sqoop** - Batch data transfer between RDBMS and HDFS
- **Apache Flume** - Log collection and aggregation
- **Hadoop HDFS** - Distributed file storage
- **MySQL** - Relational database for transactional data
- **Streamlit** - Real-time analytics dashboard
- **Docker** - Containerized deployment

### Use Case
Processing e-commerce transactions through three ingestion paths:
1. **Historical Data**: MySQL → Sqoop → HDFS (batch processing)
2. **Real-time Transactions**: Kafka → Flume → HDFS (stream processing)
3. **Application Logs**: File System → Flume → HDFS (log aggregation)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  CSV Dataset (Online Sales Data.csv)                               │
│          │                                                          │
│          ├──► Historical (70%) ──► MySQL Database                  │
│          │                            │                             │
│          └──► Realtime (30%) ───────► Kafka Stream                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    INGESTION LAYER                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐    │
│  │    Sqoop     │      │    Kafka     │      │    Flume     │    │
│  │  (Batch ETL) │      │  (Streaming) │      │(Log Collector)│    │
│  └──────┬───────┘      └──────┬───────┘      └──────┬───────┘    │
│         │                      │                      │             │
│         │ Import/Export        │ Produce/Consume     │ Spooling    │
│         │                      │                      │             │
└─────────┼──────────────────────┼──────────────────────┼─────────────┘
          │                      │                      │
          │                      ▼                      │
          │              ┌──────────────┐              │
          │              │    Flume     │              │
          │              │Kafka Consumer│              │
          │              └──────┬───────┘              │
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                    Hadoop HDFS (Data Lake)                          │
│                                                                     │
│  /user/sqoop/transactions/     - Historical batch data             │
│  /user/flume/kafka-transactions/  - Real-time streaming data       │
│  /user/flume/logs/             - Application logs                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  ANALYTICS & VISUALIZATION                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│              Streamlit Dashboard (dashboard.py)                     │
│                                                                     │
│  • Real-time metrics & KPIs                                         │
│  • Interactive charts & visualizations                              │
│  • Sales analytics & trends                                         │
│  • System health monitoring                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. MySQL Database
**Purpose**: Source database for transactional data

**Configuration**:
- **Image**: `mysql:8.0`
- **Port**: `3306`
- **Database**: `testdb`
- **Credentials**: `sqoop / sqoop123`

**Schema**:
```sql
CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY,
    customer_id VARCHAR(50),
    customer_name VARCHAR(100),
    product_id VARCHAR(50),
    product_category VARCHAR(50),
    quantity INT,
    price DECIMAL(10,2),
    total_revenue DECIMAL(10,2),
    region VARCHAR(50),
    payment_method VARCHAR(50),
    transaction_date DATE,
    INDEX idx_date (transaction_date),
    INDEX idx_category (product_category)
);
```

**Initialization**:
- SQL scripts in `mysql-init/init.sql` run automatically on container startup
- Historical transaction data loaded via `load_mysql_data.py`

---

### 2. Apache Kafka
**Purpose**: Real-time event streaming platform

**Configuration**:
- **Image**: `confluentinc/cp-kafka:7.5.0`
- **Port**: `9092` (external), `29092` (internal)
- **Zookeeper**: Required for coordination (port `2181`)

**Topics**:
- `ecommerce-transactions`: Real-time transaction events
  - **Partitions**: 3
  - **Replication Factor**: 1
  - **Format**: JSON

**Producer**:
```python
# stream_to_kafka.py
# Streams real-time transactions to Kafka
# Rate: Configurable (default: every 3 seconds)
```

**Consumer**:
- Flume Kafka consumer (`flume-kafka.conf`)
- Consumer group: `flume-consumer-group`

---

### 3. Apache Sqoop
**Purpose**: Bulk data transfer between MySQL and HDFS

**Configuration**:
- **Custom Dockerfile**: `sqoop/Dockerfile`
- **Hadoop Integration**: Connected to namenode via `hadoop.env`
- **JDBC Driver**: MySQL Connector included

**Operations**:

#### Import (MySQL → HDFS):
```bash
# Import transactions table
sqoop import \
  --connect jdbc:mysql://mysql:3306/testdb \
  --username sqoop \
  --password sqoop123 \
  --table transactions \
  --target-dir /user/sqoop/transactions \
  --num-mappers 4 \
  --delete-target-dir
```

#### Export (HDFS → MySQL):
```bash
# Export processed data back to MySQL
sqoop export \
  --connect jdbc:mysql://mysql:3306/testdb \
  --username sqoop \
  --password sqoop123 \
  --table processed_transactions \
  --export-dir /user/sqoop/processed \
  --input-fields-terminated-by ','
```

**Scripts**:
- `scripts/sqoop_import.sh` - Automates import operations
- `scripts/sqoop_export.sh` - Automates export operations

---

### 4. Apache Flume
**Purpose**: Log collection and stream aggregation

**Configuration**:
- **Custom Dockerfile**: `flume/Dockerfile`
- **Agents**: Two independent agents running

#### 4.1 Log Processing Agent
**Config**: `flume-conf/flume-logs.conf`

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Source:    │      │   Channel:   │      │    Sink:     │
│  Spooling    │ ───► │   Memory     │ ───► │    HDFS      │
│  Directory   │      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘

Source:
  - Type: Spooling Directory
  - Path: /logs/incoming
  - Delete Policy: immediate
  
Channel:
  - Type: Memory
  - Capacity: 10,000 events
  
Sink:
  - Type: HDFS
  - Path: hdfs://namenode:9000/user/flume/logs/%Y/%m/%d
  - Roll Interval: 5 minutes
```

#### 4.2 Kafka Consumer Agent
**Config**: `flume-conf/flume-kafka.conf`

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Source:    │      │   Channel:   │      │    Sink:     │
│    Kafka     │ ───► │     File     │ ───► │    HDFS      │
│   Consumer   │      │              │      │              │
└──────────────┘      └──────────────┘      └──────────────┘

Source:
  - Type: Kafka Source
  - Topic: ecommerce-transactions
  - Bootstrap Servers: kafka:29092
  
Channel:
  - Type: File (more reliable)
  - Capacity: 1,000,000 events
  
Sink:
  - Type: HDFS
  - Path: hdfs://namenode:9000/user/flume/kafka-transactions/%Y/%m/%d/%H
  - Roll Interval: 10 minutes
  - Partitioning: Year/Month/Day/Hour
```

**Management**:
- Start agents: `scripts/start_flume.sh`
- Generates logs: `scripts/generate_logs.py`

---

### 5. Hadoop HDFS
**Purpose**: Distributed file system for data lake

**Configuration**:
- **Images**: `bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8`
- **NameNode Port**: `9870` (Web UI), `9000` (RPC)
- **Cluster Name**: `bigdata-cluster`

**Directory Structure**:
```
/
├── user/
│   ├── sqoop/
│   │   └── transactions/           # Batch import from MySQL
│   │       ├── part-m-00000
│   │       ├── part-m-00001
│   │       ├── part-m-00002
│   │       └── part-m-00003
│   │
│   └── flume/
│       ├── kafka-transactions/     # Real-time streaming data
│       │   └── 2025/
│       │       └── 11/
│       │           └── 16/
│       │               ├── 10/
│       │               │   └── kafka-txn-*.json
│       │               └── 11/
│       │                   └── kafka-txn-*.json
│       │
│       └── logs/                   # Application logs
│           └── 2025/
│               └── 11/
│                   └── 16/
│                       └── ecommerce-logs-*.log
```

**Access**:
- **Web UI**: http://localhost:9870
- **HDFS Commands**: Execute via namenode container
  ```bash
  docker exec namenode hdfs dfs -ls /
  docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000
  ```

---

### 6. Streamlit Dashboard
**Purpose**: Real-time analytics and visualization

**File**: `dashboard.py`

**Features**:

#### 6.1 Overview Page
- **System Status**: Real-time Docker container health
- **Key Metrics**:
  - Total Transactions
  - Total Revenue
  - Average Transaction Value
  - Products Sold
- **Visualizations**:
  - Revenue by Category (Bar Chart)
  - Regional Distribution (Pie Chart)
  - Sales Trends (Time Series)

#### 6.2 Sales Analytics
- **Interactive Filters**:
  - Date Range Picker
  - Category Filter
  - Region Filter
  - Payment Method Filter
- **Advanced Charts**:
  - Top 10 Products by Revenue
  - Payment Method Distribution
  - Hourly Sales Patterns
  - Customer Segmentation

#### 6.3 Pipeline Status
- **Container Monitoring**:
  - MySQL, Kafka, HDFS, Sqoop, Flume status
  - Resource usage metrics
- **HDFS Browser**:
  - Navigate HDFS directories
  - View file contents
  - Download data
- **Kafka Topics**:
  - List active topics
  - View consumer groups
  - Monitor lag

#### 6.4 Real-time Streaming
- **Auto-refresh**: Configurable interval (5-60 seconds)
- **Live Indicator**: Shows last update timestamp
- **Streaming Metrics**:
  - Messages per second
  - Processing latency
  - Error rates

**Launch**:
```bash
streamlit run dashboard.py --server.port 8501
```

---

## Data Flow

### Flow 1: Historical Batch Processing
```
CSV File (shared-data/Online Sales Data.csv)
    │
    │ [split_data.py: 70% historical]
    ▼
shared-data/transactions_historical.csv
    │
    │ [generate_mysql_schema.py]
    │ [load_mysql_data.py]
    ▼
MySQL Database (testdb.transactions)
    │
    │ [sqoop_import.sh]
    │ Sqoop Import Job (4 mappers)
    ▼
HDFS (/user/sqoop/transactions/)
    │
    │ 4 part files (parallel processing)
    ▼
Dashboard Query & Visualization
```

### Flow 2: Real-time Streaming
```
CSV File (shared-data/Online Sales Data.csv)
    │
    │ [split_data.py: 30% real-time]
    ▼
shared-data/transactions_realtime.csv
    │
    │ [stream_to_kafka.py]
    │ Produce events every 3s
    ▼
Kafka Topic (ecommerce-transactions)
    │
    │ Partition 0, 1, 2 (round-robin)
    ▼
Flume Kafka Source
    │
    │ Batch: 100 events / 2s
    ▼
File Channel (checkpoint + data)
    │
    │ Reliable buffering
    ▼
HDFS Sink (time-partitioned)
    │
    │ Roll every 10 minutes
    ▼
HDFS (/user/flume/kafka-transactions/YYYY/MM/DD/HH/)
    │
    │ kafka-txn-*.json files
    ▼
Dashboard Real-time Update
```

### Flow 3: Log Aggregation
```
Application Events
    │
    │ [generate_logs.py]
    │ Creates log files
    ▼
File System (/logs/incoming/)
    │
    │ app-TIMESTAMP.log
    ▼
Flume Spooling Directory Source
    │
    │ Monitors directory
    │ Deletes after processing
    ▼
Memory Channel
    │
    │ Batch: 1000 events
    ▼
HDFS Sink (date-partitioned)
    │
    │ Roll every 5 minutes
    ▼
HDFS (/user/flume/logs/YYYY/MM/DD/)
    │
    │ ecommerce-logs-*.log files
    ▼
Log Analysis & Monitoring
```

---

## Docker Infrastructure

### Network Architecture
```
bigdata-network (Bridge Network)
    │
    ├── zookeeper:2181
    ├── kafka:29092 (internal), :9092 (external)
    ├── namenode:9000 (RPC), :9870 (Web)
    ├── datanode:50075
    ├── mysql:3306
    ├── sqoop (no exposed ports)
    ├── flume (no exposed ports)
    └── kafka-ui:8080
```

### Volume Persistence
```yaml
volumes:
  zookeeper-data:     # Zookeeper state
  zookeeper-logs:     # Zookeeper logs
  kafka-data:         # Kafka topics & partitions
  namenode-data:      # HDFS namespace
  datanode-data:      # HDFS blocks
  mysql-data:         # MySQL database files
```

### Shared Volumes (Bind Mounts)
```yaml
./shared-data:      # Mounted to namenode, datanode, flume
./flume-conf:       # Mounted to flume
./logs:             # Mounted to flume
./mysql-init:       # Mounted to mysql
```

### Container Dependencies
```
┌──────────────┐
│  Zookeeper   │
└──────┬───────┘
       │
       ▼
┌──────────────┐     ┌──────────────┐
│    Kafka     │     │   NameNode   │
└──────┬───────┘     └──────┬───────┘
       │                    │
       │                    ▼
       │             ┌──────────────┐
       │             │   DataNode   │
       │             └──────┬───────┘
       │                    │
       ├────────────────────┼────────┐
       │                    │        │
       ▼                    ▼        ▼
┌──────────────┐     ┌──────────────┐ ┌──────────────┐
│    Flume     │     │    Sqoop     │ │    MySQL     │
└──────────────┘     └──────────────┘ └──────────────┘
       │                    │
       └────────────────────┘
                  │
                  ▼
           ┌──────────────┐
           │  Kafka UI    │
           └──────────────┘
```

---

## Deployment Guide

### Prerequisites
- **Docker Desktop** with WSL2 backend (Windows) or Docker Engine (Linux)
- **Minimum Resources**: 8GB RAM, 20GB disk space
- **Python 3.8+** (for scripts)

### Installation Steps

#### 1. Clone & Setup
```bash
# Navigate to project directory
cd ~/bigdata-project  # or /mnt/c/Users/sadok/bigdata-project

# Verify files
ls -la
```

#### 2. Start Docker Infrastructure
```bash
# Start all containers
docker-compose up -d

# Verify all services are running
docker-compose ps

# Expected output: All containers with status "Up"
```

#### 3. Wait for Service Initialization
```bash
# Wait ~60 seconds for services to fully start

# Check namenode logs
docker-compose logs -f namenode
# Wait for: "NameNode RPC up at..."

# Check kafka logs
docker-compose logs -f kafka
# Wait for: "Kafka Server started"
```

#### 4. Install Python Dependencies
```bash
pip3 install --user -r requirements.txt
```

#### 5. Run Complete Pipeline
```bash
# Make scripts executable (Linux/WSL)
chmod +x scripts/*.sh

# Execute master pipeline
bash scripts/run_pipeline.sh
```

**Pipeline Steps** (automated):
1. ✅ Analyze dataset structure
2. ✅ Split data (70% historical / 30% real-time)
3. ✅ Generate MySQL schema
4. ✅ Load historical data to MySQL
5. ✅ Create Kafka topics
6. ✅ Run Sqoop import to HDFS
7. ✅ Generate application logs
8. ✅ Start Flume agents
9. ✅ Stream real-time data to Kafka
10. ✅ Verify HDFS data integrity

#### 6. Launch Dashboard
```bash
streamlit run dashboard.py
```

Dashboard opens at: **http://localhost:8501**

---

## Monitoring & Visualization

### Web Interfaces

| Service | URL | Purpose |
|---------|-----|---------|
| **HDFS NameNode** | http://localhost:9870 | HDFS cluster overview, browse files |
| **Kafka UI** | http://localhost:8080 | Kafka topics, consumer groups, messages |
| **Streamlit Dashboard** | http://localhost:8501 | Analytics & visualization |

### Command-Line Monitoring

#### Docker Health
```bash
# Container status
docker-compose ps

# Container logs
docker-compose logs -f [service_name]

# Resource usage
docker stats
```

#### Kafka Monitoring
```bash
# List topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Consumer group status
docker exec kafka kafka-consumer-groups --list --bootstrap-server localhost:9092

# Topic details
docker exec kafka kafka-topics --describe --topic ecommerce-transactions \
  --bootstrap-server localhost:9092
```

#### HDFS Monitoring
```bash
# Cluster status
docker exec namenode hdfs dfsadmin -report

# Directory listing
docker exec namenode hdfs dfs -ls -R /user

# File count and size
docker exec namenode hdfs dfs -du -s -h /user/sqoop/transactions
docker exec namenode hdfs dfs -du -s -h /user/flume
```

#### MySQL Monitoring
```bash
# Table row count
docker exec mysql mysql -usqoop -psqoop123 testdb \
  -e "SELECT COUNT(*) FROM transactions;"

# Database size
docker exec mysql mysql -usqoop -psqoop123 testdb \
  -e "SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)' \
      FROM information_schema.TABLES WHERE table_schema = 'testdb';"
```

---

## Project Scripts

### Data Preparation
| Script | Purpose |
|--------|---------|
| `analyze_dataset.py` | Analyze CSV structure and statistics |
| `split_data.py` | Split dataset into historical (70%) and real-time (30%) |
| `generate_mysql_schema.py` | Generate SQL schema from CSV columns |

### Data Loading
| Script | Purpose |
|--------|---------|
| `load_mysql_data.py` | Load historical data into MySQL |
| `kafka_setup.py` | Create and configure Kafka topics |

### Data Streaming
| Script | Purpose |
|--------|---------|
| `stream_to_kafka.py` | Stream real-time transactions to Kafka |
| `realtime_stream.py` | Alternative streaming implementation |
| `generate_logs.py` | Generate application log files |

### Sqoop Operations
| Script | Purpose |
|--------|---------|
| `sqoop_import.sh` | Import MySQL data to HDFS |
| `sqoop_export.sh` | Export HDFS data to MySQL |

### Flume Operations
| Script | Purpose |
|--------|---------|
| `start_flume.sh` | Start Flume agents (logs + Kafka) |

### Orchestration & Verification
| Script | Purpose |
|--------|---------|
| `run_pipeline.sh` | Master orchestrator - runs entire pipeline |
| `verify_hdfs.sh` | Verify HDFS data integrity |
| `monitor.py` | Real-time system monitoring |

---

## Data Storage Locations

### Source Data
- **Original CSV**: `shared-data/Online Sales Data.csv`
- **Historical Split**: `shared-data/transactions_historical.csv` (70%)
- **Realtime Split**: `shared-data/transactions_realtime.csv` (30%)

### MySQL
- **Database**: `testdb`
- **Table**: `transactions`
- **Access**: `mysql -h localhost -P 3306 -u sqoop -p`

### HDFS
- **Sqoop Imports**: `/user/sqoop/transactions/`
  - Format: CSV (comma-delimited)
  - Files: 4 part files (parallel mappers)
  
- **Kafka Streaming**: `/user/flume/kafka-transactions/YYYY/MM/DD/HH/`
  - Format: JSON
  - Partitioning: Hourly time-based
  
- **Application Logs**: `/user/flume/logs/YYYY/MM/DD/`
  - Format: Plain text logs
  - Partitioning: Daily time-based

---

## Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker-compose logs [service_name]

# Restart specific service
docker-compose restart [service_name]

# Recreate container
docker-compose up -d --force-recreate [service_name]
```

#### 2. HDFS SafeMode
```bash
# Check safe mode status
docker exec namenode hdfs dfsadmin -safemode get

# Force leave safe mode
docker exec namenode hdfs dfsadmin -safemode leave
```

#### 3. Kafka Connection Issues
```bash
# Test connectivity
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# Check if topic exists
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

#### 4. Sqoop Import Fails
```bash
# Test MySQL connection
docker exec sqoop sqoop list-databases \
  --connect jdbc:mysql://mysql:3306 \
  --username sqoop --password sqoop123

# Verify table exists
docker exec mysql mysql -usqoop -psqoop123 testdb -e "SHOW TABLES;"
```

#### 5. Flume Not Collecting Data
```bash
# Check Flume logs
docker-compose logs -f flume

# Verify source directory
docker exec flume ls -la /logs/incoming/

# Restart Flume agents
docker exec flume pkill -f flume
bash scripts/start_flume.sh
```

---

## Performance Tuning

### Kafka Optimization
```yaml
# In docker-compose.yml
KAFKA_NUM_NETWORK_THREADS: 8
KAFKA_NUM_IO_THREADS: 8
KAFKA_SOCKET_SEND_BUFFER_BYTES: 102400
KAFKA_SOCKET_RECEIVE_BUFFER_BYTES: 102400
KAFKA_LOG_RETENTION_HOURS: 168  # 7 days
```

### Sqoop Parallelism
```bash
# Increase mappers for faster import
sqoop import --num-mappers 8  # Default: 4
```

### Flume Throughput
```properties
# In flume-kafka.conf
kafka-agent.sources.kafka-source.batchSize = 1000  # Increase batch size
kafka-agent.channels.file-channel.capacity = 2000000  # Increase capacity
kafka-agent.sinks.hdfs-sink.hdfs.batchSize = 500  # Larger HDFS batches
```

### HDFS Replication
```bash
# Set replication factor (for multi-node cluster)
docker exec namenode hdfs dfs -setrep -w 3 /user/sqoop/transactions
```

---

## Security Considerations

### Current Implementation (Development)
- **MySQL**: Basic authentication (sqoop/sqoop123)
- **Kafka**: No authentication (PLAINTEXT)
- **HDFS**: Permissive mode
- **Network**: Internal Docker bridge network

### Production Recommendations
1. **Enable SSL/TLS** for Kafka, MySQL, HDFS
2. **Implement SASL** authentication for Kafka
3. **Configure Kerberos** for Hadoop
4. **Use secrets management** (Docker Secrets, HashiCorp Vault)
5. **Network segmentation** with firewall rules
6. **Enable audit logging** for all services
7. **Regular security updates** for all images

---

## Future Enhancements

### Planned Features
1. **Apache Spark** integration for advanced analytics
2. **Apache Hive** for SQL-on-Hadoop querying
3. **Apache HBase** for real-time NoSQL storage
4. **Elasticsearch** for log analytics
5. **Grafana** dashboards for infrastructure monitoring
6. **Kubernetes** deployment for production scalability
7. **Machine Learning** pipelines for predictive analytics
8. **CDC (Change Data Capture)** from MySQL using Debezium

---

## Conclusion

This Big Data platform demonstrates a complete end-to-end pipeline for processing e-commerce data using industry-standard tools. The architecture supports:

✅ **Batch Processing** via Sqoop for historical data  
✅ **Stream Processing** via Kafka for real-time events  
✅ **Log Aggregation** via Flume for application logs  
✅ **Distributed Storage** via HDFS for data lake  
✅ **Real-time Analytics** via Streamlit dashboard  

The containerized deployment ensures reproducibility and scalability, making it suitable for both learning and production use cases.

---

## Project Structure (Final)
```
bigdata-project/
├── README.md                      # Project overview
├── ARCHITECTURE.md                # This file (complete architecture)
├── docker-compose.yml             # Docker orchestration
├── hadoop.env                     # Hadoop environment variables
├── requirements.txt               # Python dependencies
├── dashboard.py                   # Streamlit analytics dashboard
│
├── scripts/                       # Automation scripts
│   ├── README.md                  # Scripts documentation
│   ├── analyze_dataset.py         # Dataset analysis
│   ├── split_data.py              # Data splitting (70/30)
│   ├── generate_mysql_schema.py   # SQL schema generation
│   ├── load_mysql_data.py         # MySQL data loading
│   ├── kafka_setup.py             # Kafka topic creation
│   ├── stream_to_kafka.py         # Real-time streaming to Kafka
│   ├── realtime_stream.py         # Alternative streaming
│   ├── generate_logs.py           # Log file generation
│   ├── sqoop_import.sh            # Sqoop import automation
│   ├── sqoop_export.sh            # Sqoop export automation
│   ├── start_flume.sh             # Flume agent startup
│   ├── verify_hdfs.sh             # HDFS verification
│   ├── run_pipeline.sh            # Master orchestrator
│   └── monitor.py                 # System monitoring
│
├── flume-conf/                    # Flume configurations
│   ├── flume-logs.conf            # Log processing agent
│   └── flume-kafka.conf           # Kafka consumer agent
│
├── mysql-init/                    # MySQL initialization
│   └── init.sql                   # Database schema
│
├── sql/                           # SQL scripts
│   └── create_tables.sql          # Table definitions
│
├── sqoop/                         # Sqoop container
│   └── Dockerfile                 # Custom Sqoop image
│
├── flume/                         # Flume container
│   └── Dockerfile                 # Custom Flume image
│
├── shared-data/                   # Shared datasets
│   ├── Online Sales Data.csv      # Original dataset
│   ├── transactions_historical.csv # Historical split
│   └── transactions_realtime.csv  # Real-time split
│
├── logs/                          # Application logs
│   └── incoming/                  # Flume spooling directory
│
└── data/                          # Additional data files
```

---

**Author**: Big Data Engineering Team  
**Last Updated**: November 16, 2025  
**Version**: 1.0.0
