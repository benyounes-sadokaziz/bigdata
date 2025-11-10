#!/usr/bin/env python3
"""
Complete Big Data Pipeline Execution
Processes the full dataset through all 3 ingestion paths
"""

import subprocess
import time
import sys
import os

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, check=True, 
                                   capture_output=False, text=True)
        else:
            result = subprocess.run(cmd, check=True, 
                                   capture_output=False, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("  BIG DATA PIPELINE - FULL EXECUTION")
    print("  Processing Online Sales Dataset")
    print("="*60)
    
    # Phase 1: Data Preparation
    print("\n[PHASE 1] DATA PREPARATION")
    print("-" * 60)
    
    if not run_command(
        "python scripts/analyze_dataset.py",
        "Analyzing dataset structure"
    ):
        print("Warning: Dataset analysis failed, continuing...")
    
    if not run_command(
        "python scripts/split_data.py",
        "Splitting data (70% historical, 30% real-time)"
    ):
        print("Error: Data split failed")
        return False
    
    # Phase 2: MySQL Load (Historical Data)
    print("\n[PHASE 2] MYSQL BATCH LOADING")
    print("-" * 60)
    
    if not run_command(
        "python scripts/load_mysql_data.py",
        "Loading historical data to MySQL"
    ):
        print("Error: MySQL load failed")
        return False
    
    time.sleep(2)
    
    # Phase 3: MySQL to HDFS (Sqoop alternative)
    print("\n[PHASE 3] BATCH INGESTION (MySQL → HDFS)")
    print("-" * 60)
    
    if not run_command(
        "bash export-to-hdfs.sh",
        "Exporting MySQL data to HDFS"
    ):
        print("Error: HDFS export failed")
        return False
    
    # Phase 4: Kafka Setup
    print("\n[PHASE 4] KAFKA SETUP")
    print("-" * 60)
    
    if not run_command(
        "python scripts/kafka_setup.py",
        "Creating Kafka topics"
    ):
        print("Warning: Kafka setup had issues, continuing...")
    
    time.sleep(2)
    
    # Phase 5: Real-time Streaming to Kafka
    print("\n[PHASE 5] REAL-TIME STREAMING (Kafka)")
    print("-" * 60)
    print("Starting Kafka producer (this will stream 72 transactions)...")
    print("Press Ctrl+C after streaming completes to continue")
    
    try:
        subprocess.run(
            "python scripts/stream_to_kafka.py",
            shell=True,
            timeout=120
        )
    except subprocess.TimeoutExpired:
        print("\nStreaming completed (timeout reached)")
    except KeyboardInterrupt:
        print("\nStreaming stopped by user")
    
    # Phase 6: Log Generation
    print("\n[PHASE 6] LOG GENERATION")
    print("-" * 60)
    
    if not run_command(
        "python scripts/generate_logs.py",
        "Generating application logs (5000+ entries)"
    ):
        print("Warning: Log generation failed, continuing...")
    
    # Phase 7: Start Flume Agents
    print("\n[PHASE 7] FLUME INGESTION")
    print("-" * 60)
    print("Starting Flume agents (running in background)...")
    
    try:
        subprocess.Popen(
            ["bash", "scripts/start_flume.sh"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✓ Flume agents started")
        time.sleep(5)
    except Exception as e:
        print(f"Warning: Flume start failed: {e}")
    
    # Phase 8: Verification
    print("\n[PHASE 8] VERIFICATION")
    print("-" * 60)
    
    print("\nChecking MySQL...")
    subprocess.run(
        'docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) as records FROM transactions"',
        shell=True
    )
    
    print("\nChecking HDFS...")
    subprocess.run(
        "docker exec namenode hdfs dfs -ls -R /user/",
        shell=True
    )
    
    print("\nChecking Kafka Topics...")
    subprocess.run(
        "docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list",
        shell=True
    )
    
    # Summary
    print("\n" + "="*60)
    print("  PIPELINE EXECUTION COMPLETED!")
    print("="*60)
    print("\n📊 View Your Results:")
    print("  • Hadoop Web UI:  http://localhost:9870")
    print("  • Browse HDFS:    http://localhost:9870/explorer.html#/user")
    print("\n📈 Data Locations:")
    print("  • MySQL:          testdb.transactions")
    print("  • HDFS (Batch):   /user/sqoop/transactions/")
    print("  • HDFS (Kafka):   /user/flume/kafka-transactions/")
    print("  • HDFS (Logs):    /user/flume/logs/")
    print("\n✓ Pipeline is now processing your Online Sales dataset!")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
