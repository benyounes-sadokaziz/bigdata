#!/usr/bin/env python3
"""
Pipeline Monitor - Phase 8.1
Real-time monitoring dashboard for the Big Data pipeline
"""

import subprocess
import time
import os
from datetime import datetime

def run_command(command):
    """Execute shell command and return output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except:
        return "Error"

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def check_container_status(container_name):
    """Check if a Docker container is running"""
    cmd = f"docker ps --filter name={container_name} --format '{{{{.Status}}}}'"
    result = run_command(cmd)
    return "✅ Running" if result else "❌ Stopped"

def get_mysql_count():
    """Get transaction count from MySQL"""
    cmd = 'docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) FROM transactions;" -s -N 2>/dev/null'
    result = run_command(cmd)
    return result if result and result != "Error" else "0"

def get_kafka_topics():
    """Get list of Kafka topics"""
    cmd = "docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null | grep ecommerce"
    result = run_command(cmd)
    return result.split('\n') if result else []

def get_hdfs_directories():
    """Get HDFS directory listing"""
    cmd = "docker exec namenode hdfs dfs -du -s /user/* 2>/dev/null"
    result = run_command(cmd)
    return result

def monitor_pipeline():
    """Main monitoring loop"""
    
    print("Starting Pipeline Monitor...")
    print("Press Ctrl+C to exit\n")
    time.sleep(2)
    
    try:
        while True:
            clear_screen()
            
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print("╔════════════════════════════════════════════════════════════╗")
            print("║     E-Commerce Big Data Pipeline - Live Monitor           ║")
            print("╚════════════════════════════════════════════════════════════╝")
            print(f"🕐 {current_time}")
            print("")
            
            # Container Status
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("CONTAINER STATUS")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"MySQL:      {check_container_status('mysql')}")
            print(f"Kafka:      {check_container_status('kafka')}")
            print(f"Zookeeper:  {check_container_status('zookeeper')}")
            print(f"Namenode:   {check_container_status('namenode')}")
            print(f"Datanode:   {check_container_status('datanode')}")
            print(f"Sqoop:      {check_container_status('sqoop')}")
            print(f"Flume:      {check_container_status('flume')}")
            print("")
            
            # MySQL Stats
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("MYSQL DATABASE")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            mysql_count = get_mysql_count()
            print(f"Total Transactions: {mysql_count}")
            print("")
            
            # Kafka Topics
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("KAFKA TOPICS")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            topics = get_kafka_topics()
            if topics:
                for topic in topics:
                    print(f"📌 {topic}")
            else:
                print("No e-commerce topics found")
            print("")
            
            # HDFS Status
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("HDFS DATA LAKE")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            hdfs_data = get_hdfs_directories()
            if hdfs_data:
                print(hdfs_data)
            else:
                print("No data in HDFS yet")
            print("")
            
            # Quick Stats
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("QUICK STATS")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            # Sqoop data count
            sqoop_count = run_command(
                "docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 2>/dev/null | wc -l"
            )
            print(f"Sqoop Records:  {sqoop_count if sqoop_count != 'Error' else '0'}")
            
            # Flume log count
            log_count = run_command(
                "docker exec namenode bash -c \"hdfs dfs -cat '/user/flume/logs/*/*/*/*.log' 2>/dev/null | wc -l\""
            )
            print(f"Flume Logs:     {log_count if log_count != 'Error' else '0'}")
            
            # Kafka data count
            kafka_count = run_command(
                "docker exec namenode bash -c \"hdfs dfs -cat '/user/flume/kafka-transactions/*/*/*/*/*.json' 2>/dev/null | wc -l\""
            )
            print(f"Kafka Records:  {kafka_count if kafka_count != 'Error' else '0'}")
            
            print("")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("Refreshing in 5 seconds... (Press Ctrl+C to exit)")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped by user")
        print("✅ Pipeline monitoring ended\n")

if __name__ == "__main__":
    monitor_pipeline()
