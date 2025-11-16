# Big Data E-Commerce Analytics Platform
## Kafka, Sqoop & Flume Integration

This project demonstrates a complete Big Data architecture for e-commerce analytics using:
- **Apache Kafka** - Real-time event streaming
- **Apache Sqoop** - Batch data transfer (MySQL ↔ HDFS)
- **Apache Flume** - Log collection and stream aggregation
- **Hadoop HDFS** - Distributed data lake
- **Streamlit** - Real-time analytics dashboard

📖 **[Complete Architecture Documentation](ARCHITECTURE.md)** - Detailed system design, data flows, and component specifications

## 📋 Prerequisites

- Windows 10/11 with WSL2 installed (or Linux/Mac)
- Docker Desktop (with WSL2 backend on Windows)
- At least 8GB RAM available for Docker
- Python 3.8+ with pip
- Basic understanding of command line

## 🏗️ Architecture Overview

```
CSV Dataset (Online Sales Data)
    │
    ├──► MySQL (Historical) ──Sqoop──▶ HDFS
    │
    ├──► Kafka (Real-time) ──Flume──▶ HDFS
    │
    └──► Logs (Application) ──Flume──▶ HDFS
```

**See [ARCHITECTURE.md](ARCHITECTURE.md) for complete system design, data flows, and component specifications.**

## 🚀 Quick Start

### 1. Start Docker Containers
```bash
# Navigate to project directory
cd ~/bigdata-project  # or /mnt/c/Users/sadok/bigdata-project

# Start all services
docker-compose up -d

# Wait ~60 seconds for initialization
sleep 60

# Verify all containers are running
docker-compose ps
```

### 2. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Run Complete Data Pipeline
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Execute the complete pipeline
bash scripts/run_pipeline.sh
```

This automated pipeline will:
1. ✅ Analyze the dataset
2. ✅ Split data (70% historical / 30% real-time)
3. ✅ Load historical data to MySQL
4. ✅ Import MySQL data to HDFS via Sqoop
5. ✅ Create Kafka topics
6. ✅ Stream real-time data to Kafka
7. ✅ Start Flume agents for log processing
8. ✅ Verify data integrity in HDFS

### 4. Launch Analytics Dashboard
```bash
streamlit run dashboard.py
```

Dashboard will open at: **http://localhost:8501**

## 📊 Dashboard Features

- **Overview**: System status, key metrics, revenue analytics
- **Sales Analytics**: Interactive charts, filters, trend analysis
- **Pipeline Status**: Container health, HDFS browser, Kafka monitoring
- **Real-time Streaming**: Auto-refresh, live data updates

## 🔍 Monitoring & Access

| Service | URL/Command | Description |
|---------|-------------|-------------|
| **HDFS Web UI** | http://localhost:9870 | Browse HDFS files and cluster status |
| **Kafka UI** | http://localhost:8080 | Monitor Kafka topics and messages |
| **Streamlit Dashboard** | http://localhost:8501 | Analytics and visualizations |
| **MySQL** | `mysql -h localhost -P 3306 -u sqoop -p` | Database access (password: sqoop123) |

## 🧪 Quick Tests

### Test Kafka
```bash
# List topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# View messages
docker exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ecommerce-transactions \
  --from-beginning --max-messages 10
```

### Test HDFS
```bash
# List all data
docker exec namenode hdfs dfs -ls -R /user

# View Sqoop imported data
docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 | head

# Check Kafka streaming data
docker exec namenode hdfs dfs -ls /user/flume/kafka-transactions
```

### Test MySQL
```bash
# Row count
docker exec mysql mysql -usqoop -psqoop123 testdb \
  -e "SELECT COUNT(*) FROM transactions;"

# Sample data
docker exec mysql mysql -usqoop -psqoop123 testdb \
  -e "SELECT * FROM transactions LIMIT 5;"
```

#### Verify logs in HDFS:
```bash
# Wait a few seconds for Flume to process
docker exec -it namenode hdfs dfs -ls -R /user/flume/logs/

# View log content
docker exec -it namenode hdfs dfs -cat /user/flume/logs/*/logs-*.log | head -20
```

#### Start Flume agent for Kafka-to-HDFS:
```bash
docker exec -d flume flume-ng agent \
  --conf /opt/flume/conf \
  --conf-file /opt/flume/conf/flume-kafka-hdfs.conf \
  --name agent2 \
  -Dflume.root.logger=INFO,console
```

#### Send data to Kafka (will be picked up by Flume):
```bash
docker exec -it kafka bash -c "echo 'Sample message from Kafka to HDFS via Flume' | kafka-console-producer --bootstrap-server localhost:9092 --topic test-topic"
```

#### Check data in HDFS:
```bash
docker exec -it namenode hdfs dfs -ls -R /user/flume/kafka-data/
```

## 🌐 Web Interfaces

- **Kafka UI**: http://localhost:8080
- **Hadoop NameNode**: http://localhost:9870

## 📊 Complete Integration Test

This test combines all three tools:

```bash
# 1. Create a Kafka topic for sales data
docker exec -it kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic sales-stream \
  --partitions 1 \
  --replication-factor 1

# 2. Import sales data from MySQL to HDFS using Sqoop
docker exec -it sqoop sqoop import \
  --connect jdbc:mysql://mysql:3306/testdb \
  --username sqoop \
  --password sqoop123 \
  --table sales \
  --target-dir /user/integration/mysql-sales \
  --m 1

# 3. Send real-time sales updates to Kafka
docker exec -it kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic sales-stream << EOF
{"product":"Laptop","quantity":2,"price":1200,"region":"North"}
{"product":"Mouse","quantity":5,"price":25,"region":"South"}
{"product":"Monitor","quantity":1,"price":350,"region":"East"}
EOF

# 4. Generate application logs

## 📁 Project Structure

```
bigdata-project/
├── README.md                    # This file - Quick start guide
├── ARCHITECTURE.md              # Complete architecture documentation
├── docker-compose.yml           # Docker orchestration
├── hadoop.env                   # Hadoop configuration
├── requirements.txt             # Python dependencies
├── dashboard.py                 # Streamlit analytics dashboard
│
├── scripts/                     # Automation scripts
│   ├── analyze_dataset.py       # Dataset analysis
│   ├── split_data.py            # Data splitting (70/30)
│   ├── load_mysql_data.py       # MySQL data loading
│   ├── kafka_setup.py           # Kafka topic creation
│   ├── stream_to_kafka.py       # Real-time streaming
│   ├── generate_logs.py         # Log generation
│   ├── sqoop_import.sh          # Sqoop import automation
│   ├── start_flume.sh           # Flume agent startup
│   ├── run_pipeline.sh          # Master orchestrator
│   └── verify_hdfs.sh           # HDFS verification
│
├── flume-conf/                  # Flume configurations
│   ├── flume-logs.conf          # Log processing agent
│   └── flume-kafka.conf         # Kafka consumer agent
│
├── mysql-init/                  # MySQL initialization
│   └── init.sql                 # Database schema
│
├── sqoop/                       # Sqoop Docker image
│   └── Dockerfile
│
├── flume/                       # Flume Docker image
│   └── Dockerfile
│
├── shared-data/                 # Datasets
│   ├── Online Sales Data.csv    # Original dataset
│   ├── transactions_historical.csv  # Historical (70%)
│   └── transactions_realtime.csv    # Real-time (30%)
│
└── logs/                        # Application logs
    └── incoming/                # Flume spooling directory
```

## 🔧 Useful Commands

### Docker Management
```bash
# View logs
docker-compose logs -f [service_name]

# Restart services
docker-compose restart

# Stop/Start
docker-compose stop
docker-compose start

# Clean up
docker-compose down -v
```

### HDFS Operations
```bash
# List files
docker exec namenode hdfs dfs -ls -R /user

# View file content
docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 | head

# Upload/Download
docker exec namenode hdfs dfs -put /shared-data/file.txt /user/test/
docker exec namenode hdfs dfs -get /user/test/file.txt /shared-data/
```

### Kafka Operations
```bash
# List topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Describe topic
docker exec kafka kafka-topics --describe --topic ecommerce-transactions \
  --bootstrap-server localhost:9092

# View consumer groups
docker exec kafka kafka-consumer-groups --list --bootstrap-server localhost:9092
```

## 🐛 Troubleshooting

### Containers Won't Start
```bash
# Check logs
docker-compose logs [service_name]

# Ensure adequate resources (8GB RAM minimum)
# Restart Docker Desktop
```

### HDFS SafeMode Issues
```bash
# Check safe mode status
docker exec namenode hdfs dfsadmin -safemode get

# Force leave safe mode
docker exec namenode hdfs dfsadmin -safemode leave
```

### Kafka Connection Issues
```bash
# Verify Zookeeper
docker exec zookeeper bash -c "echo stat | nc localhost 2181"

# Test Kafka broker
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```


## 📚 Additional Resources

- **[Complete Architecture Documentation](ARCHITECTURE.md)** - Detailed system design
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Sqoop Documentation](https://sqoop.apache.org/docs/1.4.7/)
- [Apache Flume Documentation](https://flume.apache.org/documentation.html)
- [Hadoop HDFS Documentation](https://hadoop.apache.org/docs/current/)

## 🆘 Support

If you encounter issues:
1. Check container logs: `docker-compose logs [service-name]`
2. Verify all containers: `docker-compose ps`
3. Review [ARCHITECTURE.md](ARCHITECTURE.md) troubleshooting section
4. Ensure Docker has adequate resources (8GB+ RAM)

---

**Project**: Big Data E-Commerce Analytics Platform  
**Technologies**: Kafka, Sqoop, Flume, Hadoop, MySQL, Streamlit  
**License**: MIT  
**Last Updated**: November 16, 2025

