# Big Data Project - Kafka, Sqoop & Flume
## Complete Docker-based Setup for Windows/WSL

This project demonstrates a complete Big Data architecture using Kafka (real-time streaming), Sqoop (RDBMS-HDFS integration), and Flume (log processing).

## 📋 Prerequisites

- Windows 10/11 with WSL2 installed
- Docker Desktop for Windows (with WSL2 backend enabled)
- At least 8GB RAM available for Docker
- Basic understanding of command line

## 🏗️ Architecture Overview

```
MySQL (Source DB) ──Sqoop──▶ HDFS (Data Lake)
                              ▲
Log Files ──Flume──▶──────────┤
                              │
Kafka (Streaming) ──Flume──▶──┘
```

### Components:
1. **Kafka** - Real-time data streaming platform
2. **Sqoop** - Bulk data transfer between RDBMS and HDFS
3. **Flume** - Log file collection and aggregation
4. **Hadoop HDFS** - Distributed file system
5. **MySQL** - Source relational database
6. **Zookeeper** - Kafka coordination service

## 🚀 Quick Start Guide

### Step 1: Setup in WSL

Open WSL terminal and navigate to your project directory:

```bash
# Open WSL
wsl

# Create project directory
mkdir -p ~/bigdata-project
cd ~/bigdata-project

# Copy all project files here (the docker-compose.yml and all directories)
```

### Step 2: Start the Environment

```bash
# Build and start all containers
docker-compose up -d

# Check if all containers are running
docker-compose ps

# You should see all containers with status "Up"
```

### Step 3: Wait for Services to Initialize

```bash
# Wait ~60 seconds for all services to start properly
# Check logs to ensure no errors
docker-compose logs -f namenode
# Press Ctrl+C when you see "NameNode RPC up at..."

docker-compose logs -f kafka
# Press Ctrl+C when you see "Kafka Server started"
```

## 🧪 Testing Each Component

### 1️⃣ Testing Kafka (Real-time Streaming)

#### Create a topic:
```bash
docker exec -it kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic test-topic \
  --partitions 3 \
  --replication-factor 1
```

#### List topics:
```bash
docker exec -it kafka kafka-topics --list \
  --bootstrap-server localhost:9092
```

#### Send messages (Producer):
```bash
docker exec -it kafka kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic test-topic
```
Type some messages and press Enter after each. Press Ctrl+C to exit.

#### Consume messages (Consumer):
```bash
# Open a new terminal
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic test-topic \
  --from-beginning
```

#### Access Kafka UI:
Open browser: http://localhost:8080

### 2️⃣ Testing Sqoop (MySQL to HDFS)

#### Check MySQL connection:
```bash
docker exec -it sqoop sqoop list-databases \
  --connect jdbc:mysql://mysql:3306 \
  --username sqoop \
  --password sqoop123
```

#### View sample data in MySQL:
```bash
docker exec -it mysql mysql -usqoop -psqoop123 testdb \
  -e "SELECT * FROM employees LIMIT 5;"
```

#### Import employees table to HDFS:
```bash
docker exec -it sqoop sqoop import \
  --connect jdbc:mysql://mysql:3306/testdb \
  --username sqoop \
  --password sqoop123 \
  --table employees \
  --target-dir /user/sqoop/employees \
  --m 1
```

#### Verify data in HDFS:
```bash
# List directories in HDFS
docker exec -it namenode hdfs dfs -ls /user/sqoop/

# View imported data
docker exec -it namenode hdfs dfs -cat /user/sqoop/employees/part-m-00000 | head -10
```

#### Import with WHERE clause (IT department only):
```bash
docker exec -it sqoop sqoop import \
  --connect jdbc:mysql://mysql:3306/testdb \
  --username sqoop \
  --password sqoop123 \
  --table employees \
  --where "department='IT'" \
  --target-dir /user/sqoop/employees_it \
  --m 1
```

#### Import all tables:
```bash
docker exec -it sqoop sqoop import-all-tables \
  --connect jdbc:mysql://mysql:3306/testdb \
  --username sqoop \
  --password sqoop123 \
  --warehouse-dir /user/sqoop/warehouse \
  --m 1
```

### 3️⃣ Testing Flume (Log Processing)

#### Start Flume agent for log file processing:
```bash
docker exec -d flume flume-ng agent \
  --conf /opt/flume/conf \
  --conf-file /opt/flume/conf/flume-hdfs.conf \
  --name agent1 \
  -Dflume.root.logger=INFO,console
```

#### Generate sample log files:
```bash
# Copy the log generator script to the container
docker cp generate-logs.sh flume:/tmp/

# Execute it
docker exec -it flume bash /tmp/generate-logs.sh
```

#### Check Flume logs:
```bash
docker exec -it flume bash -c "tail -f /opt/flume/logs/*.log"
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
docker exec -it flume bash /tmp/generate-logs.sh

# 5. Verify all data in HDFS
docker exec -it namenode hdfs dfs -ls -R /user/
```

## 🔍 Useful Commands

### Docker Management
```bash
# View all container logs
docker-compose logs -f

# View specific container logs
docker-compose logs -f kafka

# Restart all services
docker-compose restart

# Stop all services
docker-compose stop

# Start all services
docker-compose start

# Rebuild containers (after config changes)
docker-compose up -d --build

# Remove all containers and volumes
docker-compose down -v
```

### HDFS Commands
```bash
# Create directory
docker exec -it namenode hdfs dfs -mkdir -p /user/test

# Upload file
docker exec -it namenode hdfs dfs -put /shared-data/myfile.txt /user/test/

# Download file
docker exec -it namenode hdfs dfs -get /user/test/myfile.txt /shared-data/

# View file content
docker exec -it namenode hdfs dfs -cat /user/test/myfile.txt

# Remove file/directory
docker exec -it namenode hdfs dfs -rm -r /user/test
```

### Kafka Commands
```bash
# Describe topic
docker exec -it kafka kafka-topics --describe \
  --bootstrap-server localhost:9092 \
  --topic test-topic

# Delete topic
docker exec -it kafka kafka-topics --delete \
  --bootstrap-server localhost:9092 \
  --topic test-topic

# Consumer groups
docker exec -it kafka kafka-consumer-groups --list \
  --bootstrap-server localhost:9092
```

### MySQL Commands
```bash
# Connect to MySQL
docker exec -it mysql mysql -usqoop -psqoop123 testdb

# View all tables
docker exec -it mysql mysql -usqoop -psqoop123 testdb -e "SHOW TABLES;"

# Insert new data
docker exec -it mysql mysql -usqoop -psqoop123 testdb -e \
  "INSERT INTO employees (first_name, last_name, email, department, salary, hire_date) \
   VALUES ('Test', 'User', 'test@company.com', 'IT', 90000, '2024-01-01');"
```

## 🐛 Troubleshooting

### Containers not starting:
```bash
# Check logs for errors
docker-compose logs

# Ensure Docker has enough resources (8GB RAM minimum)
# Restart Docker Desktop
```

### Kafka connection issues:
```bash
# Verify Zookeeper is running
docker exec -it zookeeper bash -c "echo stat | nc localhost 2181"

# Check Kafka broker
docker exec -it kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

### HDFS connection issues:
```bash
# Check NameNode status
docker exec -it namenode hdfs dfsadmin -report

# Verify HDFS is healthy
docker exec -it namenode hdfs dfs -ls /
```

### Sqoop import fails:
```bash
# Test MySQL connection
docker exec -it mysql mysql -usqoop -psqoop123 -e "SELECT 1;"

# Verify HDFS is accessible from Sqoop
docker exec -it sqoop hdfs dfs -ls /
```

## 📁 Project Structure

```
bigdata-project/
├── docker-compose.yml          # Main orchestration file
├── hadoop.env                  # Hadoop configuration
├── sqoop/
│   └── Dockerfile             # Sqoop image build
├── flume/
│   └── Dockerfile             # Flume image build
├── flume-conf/
│   ├── flume-hdfs.conf        # Log to HDFS config
│   └── flume-kafka-hdfs.conf  # Kafka to HDFS config
├── mysql-init/
│   └── init.sql               # Database initialization
├── sqoop-scripts/
│   └── examples.sh            # Sqoop example commands
├── logs/
│   └── incoming/              # Log files for Flume
├── shared-data/               # Shared volume
└── generate-logs.sh           # Log generator script
```

## 🎯 Project Deliverables Checklist

For your Big Data project submission:

- [ ] PowerPoint presentation covering:
  - [ ] Why Big Data is needed for your use case
  - [ ] Where Big Data is applied
  - [ ] How Big Data is used
  - [ ] Installation steps for Kafka, Sqoop, and Flume
  - [ ] Your specific use case
  
- [ ] Live demonstration showing:
  - [ ] Kafka producing and consuming messages
  - [ ] Sqoop importing data from MySQL to HDFS
  - [ ] Flume processing log files to HDFS
  
- [ ] Documentation annexe with:
  - [ ] Installation instructions (this README)
  - [ ] Configuration files
  - [ ] Screenshots of working system
  - [ ] Any challenges faced and solutions

## 💡 Tips for Your Presentation

1. **Kafka Demo**: Show real-time message streaming using the Kafka UI
2. **Sqoop Demo**: Import a table and show the before/after in MySQL and HDFS
3. **Flume Demo**: Generate logs and show them appearing in HDFS
4. **Integration**: Demonstrate how all three tools work together in a pipeline

## 📚 Additional Resources

- Apache Kafka: https://kafka.apache.org/documentation/
- Apache Sqoop: https://sqoop.apache.org/docs/1.4.7/
- Apache Flume: https://flume.apache.org/documentation.html
- Hadoop HDFS: https://hadoop.apache.org/docs/current/

## 🆘 Need Help?

If you encounter issues:
1. Check the container logs: `docker-compose logs [service-name]`
2. Verify all containers are running: `docker-compose ps`
3. Ensure Docker has sufficient resources
4. Review the troubleshooting section above

Good luck with your Big Data project! 🚀
