"""
Real-time Data Streaming Script
Continuously generates and streams data to Kafka for real-time dashboard updates
"""

import pandas as pd
import mysql.connector
from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample product data for realistic transactions
PRODUCTS = [
    {"name": "Laptop", "category": "Electronics", "price_range": (500, 2000)},
    {"name": "Smartphone", "category": "Electronics", "price_range": (200, 1200)},
    {"name": "Headphones", "category": "Electronics", "price_range": (30, 300)},
    {"name": "T-Shirt", "category": "Clothing", "price_range": (15, 50)},
    {"name": "Jeans", "category": "Clothing", "price_range": (30, 100)},
    {"name": "Sneakers", "category": "Clothing", "price_range": (40, 200)},
    {"name": "Coffee Maker", "category": "Home", "price_range": (30, 150)},
    {"name": "Blender", "category": "Home", "price_range": (25, 100)},
    {"name": "Desk Lamp", "category": "Home", "price_range": (20, 80)},
    {"name": "Book", "category": "Books", "price_range": (10, 40)},
]

REGIONS = ["North", "South", "East", "West", "Central"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "Cash"]

class RealtimeStreamer:
    def __init__(self):
        self.kafka_producer = None
        self.mysql_conn = None
        self.transaction_id = self.get_last_transaction_id() + 1
        
    def get_last_transaction_id(self):
        """Get the last transaction ID from MySQL"""
        try:
            conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='rootpassword',
                database='ecommerce'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(transaction_id) FROM transactions")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result[0] else 1000
        except Exception as e:
            logger.warning(f"Could not get last transaction ID: {e}")
            return 1000
    
    def connect_kafka(self):
        """Initialize Kafka producer"""
        try:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3
            )
            logger.info("✅ Connected to Kafka")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to Kafka: {e}")
            return False
    
    def connect_mysql(self):
        """Initialize MySQL connection"""
        try:
            self.mysql_conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='rootpassword',
                database='ecommerce'
            )
            logger.info("✅ Connected to MySQL")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to MySQL: {e}")
            return False
    
    def generate_transaction(self):
        """Generate a realistic transaction"""
        product = random.choice(PRODUCTS)
        quantity = random.randint(1, 5)
        unit_price = round(random.uniform(*product["price_range"]), 2)
        total_amount = round(quantity * unit_price, 2)
        
        transaction = {
            "transaction_id": self.transaction_id,
            "product_name": product["name"],
            "category": product["category"],
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": total_amount,
            "payment_method": random.choice(PAYMENT_METHODS),
            "region": random.choice(REGIONS),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.transaction_id += 1
        return transaction
    
    def send_to_kafka(self, transaction):
        """Send transaction to Kafka"""
        try:
            future = self.kafka_producer.send('ecommerce-transactions', transaction)
            future.get(timeout=10)
            logger.info(f"📤 Sent to Kafka: Transaction #{transaction['transaction_id']}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to send to Kafka: {e}")
            return False
    
    def save_to_mysql(self, transaction):
        """Save transaction to MySQL"""
        try:
            cursor = self.mysql_conn.cursor()
            sql = """
                INSERT INTO transactions 
                (transaction_id, product_name, category, quantity, unit_price, 
                 total_amount, payment_method, region, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                transaction['transaction_id'],
                transaction['product_name'],
                transaction['category'],
                transaction['quantity'],
                transaction['unit_price'],
                transaction['total_amount'],
                transaction['payment_method'],
                transaction['region'],
                transaction['timestamp']
            )
            cursor.execute(sql, values)
            self.mysql_conn.commit()
            logger.info(f"💾 Saved to MySQL: Transaction #{transaction['transaction_id']}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save to MySQL: {e}")
            self.mysql_conn.rollback()
            return False
    
    def stream_data(self, interval=3, duration=None):
        """
        Stream data continuously
        Args:
            interval: Seconds between transactions (default: 3)
            duration: Total duration in seconds (None = infinite)
        """
        logger.info("🚀 Starting real-time data streaming...")
        logger.info(f"⏱️  Interval: {interval} seconds per transaction")
        if duration:
            logger.info(f"⏱️  Duration: {duration} seconds")
        else:
            logger.info("⏱️  Duration: Infinite (Press Ctrl+C to stop)")
        
        # Connect to services
        if not self.connect_kafka():
            logger.error("Cannot proceed without Kafka connection")
            return
        
        if not self.connect_mysql():
            logger.error("Cannot proceed without MySQL connection")
            return
        
        start_time = time.time()
        transaction_count = 0
        
        try:
            while True:
                # Check duration
                if duration and (time.time() - start_time) >= duration:
                    logger.info(f"⏰ Reached duration limit of {duration} seconds")
                    break
                
                # Generate and send transaction
                transaction = self.generate_transaction()
                
                # Send to both Kafka and MySQL
                kafka_success = self.send_to_kafka(transaction)
                mysql_success = self.save_to_mysql(transaction)
                
                if kafka_success and mysql_success:
                    transaction_count += 1
                    logger.info(f"✅ Transaction #{transaction['transaction_id']} processed successfully")
                    logger.info(f"   Product: {transaction['product_name']} | "
                              f"Amount: ${transaction['total_amount']} | "
                              f"Region: {transaction['region']}")
                
                # Wait before next transaction
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("\n⚠️  Streaming stopped by user (Ctrl+C)")
        except Exception as e:
            logger.error(f"❌ Error during streaming: {e}")
        finally:
            self.cleanup()
            logger.info(f"📊 Total transactions streamed: {transaction_count}")
            logger.info(f"⏱️  Total time: {int(time.time() - start_time)} seconds")
    
    def cleanup(self):
        """Clean up connections"""
        if self.kafka_producer:
            self.kafka_producer.flush()
            self.kafka_producer.close()
            logger.info("🔌 Kafka producer closed")
        
        if self.mysql_conn:
            self.mysql_conn.close()
            logger.info("🔌 MySQL connection closed")

def main():
    """Main execution function"""
    print("=" * 70)
    print("🌊 REAL-TIME DATA STREAMING")
    print("=" * 70)
    print()
    print("This script continuously generates transactions and sends them to:")
    print("  • Kafka topic: ecommerce-transactions")
    print("  • MySQL database: ecommerce.transactions")
    print()
    print("Press Ctrl+C to stop streaming")
    print("=" * 70)
    print()
    
    # Create streamer
    streamer = RealtimeStreamer()
    
    # Stream data (3 seconds per transaction, infinite duration)
    streamer.stream_data(interval=3, duration=None)

if __name__ == "__main__":
    main()
