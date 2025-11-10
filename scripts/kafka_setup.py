#!/usr/bin/env python3
"""
Kafka Topic Manager - Phase 3.1
Creates and configures Kafka topics for e-commerce data streaming
"""

from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError, KafkaError
import os
import time

def wait_for_kafka(bootstrap_servers, max_retries=30):
    """Wait for Kafka to be ready"""
    print("⏳ Waiting for Kafka to be ready...")
    for i in range(max_retries):
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=bootstrap_servers,
                request_timeout_ms=5000
            )
            admin_client.close()
            print("✓ Kafka is ready!\n")
            return True
        except Exception as e:
            if i < max_retries - 1:
                print(f"  Attempt {i+1}/{max_retries} - Kafka not ready yet, waiting...")
                time.sleep(2)
            else:
                print(f"❌ Error: {e}")
                return False
    return False

def create_topics():
    """Create Kafka topics for the e-commerce platform"""
    
    # Kafka configuration
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          Kafka Topic Manager                               ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print(f"📡 Bootstrap servers: {KAFKA_BOOTSTRAP_SERVERS}\n")
    
    # Wait for Kafka
    if not wait_for_kafka(KAFKA_BOOTSTRAP_SERVERS):
        print("❌ Error: Could not connect to Kafka")
        return
    
    try:
        # Create admin client
        admin_client = KafkaAdminClient(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            request_timeout_ms=10000
        )
        
        # Define topics
        topics = [
            NewTopic(
                name='ecommerce-transactions',
                num_partitions=3,
                replication_factor=1
            ),
            NewTopic(
                name='ecommerce-logs',
                num_partitions=2,
                replication_factor=1
            ),
            NewTopic(
                name='ecommerce-analytics',
                num_partitions=2,
                replication_factor=1
            )
        ]
        
        print(f"{'='*60}")
        print("CREATING TOPICS")
        print('='*60)
        
        # Create topics
        for topic in topics:
            try:
                admin_client.create_topics([topic], validate_only=False)
                print(f"✓ Created topic: {topic.name}")
                print(f"  ├─ Partitions: {topic.num_partitions}")
                print(f"  └─ Replication Factor: {topic.replication_factor}\n")
            except TopicAlreadyExistsError:
                print(f"⚠️  Topic already exists: {topic.name}\n")
            except Exception as e:
                print(f"❌ Error creating topic {topic.name}: {e}\n")
        
        # List all topics
        print(f"{'='*60}")
        print("ALL KAFKA TOPICS")
        print('='*60)
        
        topics_metadata = admin_client.list_topics()
        for topic in sorted(topics_metadata):
            if not topic.startswith('__'):  # Skip internal topics
                topic_details = admin_client.describe_topics([topic])[0]
                print(f"📌 {topic}")
                print(f"  └─ Partitions: {len(topic_details['partitions'])}")
        
        admin_client.close()
        
        print(f"\n{'='*60}")
        print("✅ Kafka topics configured successfully!")
        print('='*60)
        print("\nNext steps:")
        print("  1. Start streaming: python3 scripts/stream_to_kafka.py")
        print("  2. Test consumer: python3 scripts/test_kafka_consumer.py")
        
    except KafkaError as e:
        print(f"\n❌ Kafka Error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    create_topics()
