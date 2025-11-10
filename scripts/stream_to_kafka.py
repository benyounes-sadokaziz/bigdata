#!/usr/bin/env python3
"""
Kafka Transaction Streamer - Phase 3.2
Streams real-time transactions from CSV to Kafka topic
"""

import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import time
import argparse
import os
from pathlib import Path
from datetime import datetime

def stream_to_kafka(csv_file, topic='ecommerce-transactions', delay=2, batch_size=1):
    """
    Stream transactions from CSV to Kafka
    
    Args:
        csv_file: Path to CSV file with transactions
        topic: Kafka topic name
        delay: Seconds between batches
        batch_size: Records to send before sleeping
    """
    
    # Kafka configuration
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          Kafka Transaction Streamer                        ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print(f"📡 Kafka Bootstrap: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"📌 Topic: {topic}")
    print(f"📊 Source: {csv_file}")
    print(f"⏱️  Delay: {delay} seconds/batch")
    print(f"📦 Batch size: {batch_size} records\n")
    
    # Check if file exists
    if not os.path.exists(csv_file):
        print(f"❌ Error: File not found: {csv_file}")
        return
    
    # Read the CSV
    print(f"📖 Loading data from CSV...")
    df = pd.read_csv(csv_file)
    total_records = len(df)
    print(f"✓ Loaded {total_records:,} records\n")
    
    try:
        # Create Kafka producer
        print("🔌 Connecting to Kafka...")
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3
        )
        print("✓ Connected to Kafka\n")
        
        print(f"{'='*60}")
        print("STREAMING STARTED")
        print('='*60)
        print("Press Ctrl+C to stop\n")
        
        records_sent = 0
        
        # Stream records
        for idx, row in df.iterrows():
            # Create transaction record with metadata
            transaction = {
                'transaction_id': str(row['Transaction ID']),
                'date': str(row['Date']),
                'product_category': str(row['Product Category']),
                'product_name': str(row['Product Name']),
                'units_sold': int(row['Units Sold']),
                'unit_price': float(row['Unit Price']),
                'total_revenue': float(row['Total Revenue']),
                'region': str(row['Region']),
                'payment_method': str(row['Payment Method']),
                # Add streaming metadata
                'streaming_timestamp': datetime.now().isoformat(),
                'record_number': idx + 1,
                'event_type': 'NEW_ORDER'
            }
            
            # Send to Kafka
            future = producer.send(topic, value=transaction)
            
            try:
                record_metadata = future.get(timeout=10)
                records_sent += 1
                
                # Print progress
                if records_sent % batch_size == 0 or records_sent == total_records:
                    progress_pct = (records_sent / total_records) * 100
                    print(f"✓ Sent {records_sent:,}/{total_records:,} records ({progress_pct:.1f}%) - "
                          f"Partition: {record_metadata.partition}, "
                          f"Offset: {record_metadata.offset}")
                    
                    # Sleep between batches
                    if records_sent < total_records:
                        time.sleep(delay)
                
            except KafkaError as e:
                print(f"❌ Failed to send record {idx}: {e}")
        
        # Ensure all messages are sent
        producer.flush()
        
        print(f"\n{'='*60}")
        print("STREAMING COMPLETED")
        print('='*60)
        print(f"✅ Successfully streamed {records_sent:,} records to topic '{topic}'")
        print(f"📊 Total time: {records_sent * delay / 60:.1f} minutes (estimated)")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Streaming interrupted by user")
        print(f"📊 Sent {records_sent:,}/{total_records:,} records before stopping")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        if 'producer' in locals():
            producer.close()
            print("\n🔌 Kafka producer closed")

def main():
    parser = argparse.ArgumentParser(description='Stream CSV data to Kafka')
    parser.add_argument('csv_file', nargs='?', help='Path to CSV file')
    parser.add_argument('topic', nargs='?', default='ecommerce-transactions', help='Kafka topic name')
    parser.add_argument('--delay', type=float, default=2, help='Seconds between batches (default: 2)')
    parser.add_argument('--batch-size', type=int, default=1, help='Records per batch (default: 1)')
    
    args = parser.parse_args()
    
    # Use default file if not provided
    if not args.csv_file:
        data_dir = Path("/shared-data") if os.path.exists("/shared-data") else Path("shared-data")
        args.csv_file = str(data_dir / "transactions_realtime.csv")
    
    stream_to_kafka(args.csv_file, args.topic, args.delay, args.batch_size)

if __name__ == "__main__":
    main()
