#!/usr/bin/env python3
"""
Kafka Consumer Tester - Phase 3.3
Tests Kafka streaming by consuming and displaying messages
"""

from kafka import KafkaConsumer
from kafka.errors import KafkaError
import json
import argparse
import os
from datetime import datetime

def test_consumer(topic='ecommerce-transactions', max_messages=10, from_beginning=True):
    """
    Consume and display messages from Kafka topic
    
    Args:
        topic: Kafka topic name
        max_messages: Maximum messages to consume (0 for unlimited)
        from_beginning: Start from earliest message
    """
    
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          Kafka Consumer Tester                             ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print(f"📡 Bootstrap servers: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"📌 Topic: {topic}")
    print(f"📊 Max messages: {max_messages if max_messages > 0 else 'Unlimited'}")
    print(f"⏮️  From beginning: {from_beginning}\n")
    
    try:
        # Create consumer
        print("🔌 Connecting to Kafka...")
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest' if from_beginning else 'latest',
            enable_auto_commit=True,
            group_id='test-consumer-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        print("✓ Connected to Kafka\n")
        
        print(f"{'='*60}")
        print("CONSUMING MESSAGES")
        print('='*60)
        print("Press Ctrl+C to stop\n")
        
        message_count = 0
        
        for message in consumer:
            message_count += 1
            
            # Display message info
            print(f"\n📨 Message {message_count}")
            print(f"├─ Partition: {message.partition}")
            print(f"├─ Offset: {message.offset}")
            print(f"├─ Timestamp: {datetime.fromtimestamp(message.timestamp/1000).isoformat()}")
            print(f"└─ Value:")
            
            # Pretty print JSON
            print(json.dumps(message.value, indent=2))
            print("-" * 60)
            
            # Stop if reached max messages
            if max_messages > 0 and message_count >= max_messages:
                print(f"\n✓ Reached maximum message count ({max_messages})")
                break
        
        print(f"\n{'='*60}")
        print(f"✅ Total messages consumed: {message_count}")
        print('='*60)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Consumer interrupted by user")
        print(f"📊 Consumed {message_count} messages before stopping")
        
    except KafkaError as e:
        print(f"\n❌ Kafka Error: {e}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        if 'consumer' in locals():
            consumer.close()
            print("\n🔌 Kafka consumer closed")

def main():
    parser = argparse.ArgumentParser(description='Test Kafka consumer')
    parser.add_argument('--topic', default='ecommerce-transactions', help='Kafka topic name')
    parser.add_argument('--max', type=int, default=10, help='Maximum messages to consume (0=unlimited)')
    parser.add_argument('--latest', action='store_true', help='Start from latest (default: earliest)')
    
    args = parser.parse_args()
    
    test_consumer(args.topic, args.max, not args.latest)

if __name__ == "__main__":
    main()
