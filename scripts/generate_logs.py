#!/usr/bin/env python3
"""
Application Log Generator - Phase 4.1
Generates realistic application logs from transaction data
"""

import pandas as pd
import random
import argparse
import os
from pathlib import Path
from datetime import datetime, timedelta

# Log level distribution
LOG_LEVELS = {
    'INFO': 0.70,
    'WARN': 0.20,
    'ERROR': 0.10
}

# Service names
SERVICES = [
    'TransactionService',
    'PaymentService',
    'InventoryService',
    'NotificationService',
    'OrderService',
    'ShippingService'
]

def get_log_level():
    """Get random log level based on distribution"""
    rand = random.random()
    cumulative = 0
    for level, prob in LOG_LEVELS.items():
        cumulative += prob
        if rand <= cumulative:
            return level
    return 'INFO'

def generate_log_message(row, log_level):
    """Generate log message based on transaction data and log level"""
    
    txn_id = row['Transaction ID']
    product = row['Product Name']
    category = row['Product Category']
    units = row['Units Sold']
    amount = row['Total Revenue']
    payment = row['Payment Method']
    region = row['Region']
    
    service = random.choice(SERVICES)
    
    if log_level == 'ERROR':
        error_messages = [
            f"Payment declined for transaction #{txn_id}: Insufficient funds",
            f"Inventory check failed for product '{product}': Database timeout",
            f"Failed to send order confirmation for transaction #{txn_id}: SMTP error",
            f"Shipping address validation failed for transaction #{txn_id}: Invalid postal code",
            f"Payment gateway error for transaction #{txn_id}: Connection timeout",
        ]
        message = random.choice(error_messages)
        
    elif log_level == 'WARN':
        warn_messages = [
            f"Low stock alert for product '{product}': {random.randint(1, 10)} units remaining",
            f"High transaction volume detected in {region}: {random.randint(100, 500)} orders/minute",
            f"Payment processing delay for transaction #{txn_id}: {random.randint(2, 5)} seconds",
            f"Product '{product}' approaching reorder point in {region}",
            f"Unusual transaction pattern detected for payment method: {payment}",
        ]
        message = random.choice(warn_messages)
        
    else:  # INFO
        info_messages = [
            f"Processing order #{txn_id} - {product} x{units}",
            f"Payment authorized for transaction #{txn_id}: ${amount:.2f} via {payment}",
            f"Stock updated for product '{product}': -{units} units",
            f"Order confirmation sent for transaction #{txn_id}",
            f"Shipping label generated for transaction #{txn_id} to {region}",
            f"Transaction #{txn_id} completed successfully - Total: ${amount:.2f}",
            f"Inventory check passed for '{product}' in category {category}",
        ]
        message = random.choice(info_messages)
    
    return service, message

def generate_logs(csv_file, output_dir='logs/incoming', logs_per_file=1000, num_files=5):
    """
    Generate application logs from transaction data
    
    Args:
        csv_file: Source CSV file
        output_dir: Output directory for log files
        logs_per_file: Number of log entries per file
        num_files: Total number of log files to generate
    """
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          Application Log Generator                         ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_path}")
    
    # Read CSV
    if not os.path.exists(csv_file):
        print(f"❌ Error: File not found: {csv_file}")
        return
    
    print(f"📖 Loading data from {csv_file}...")
    df = pd.read_csv(csv_file)
    print(f"✓ Loaded {len(df):,} transactions\n")
    
    print(f"{'='*60}")
    print("GENERATING LOG FILES")
    print('='*60)
    
    total_logs = logs_per_file * num_files
    logs_generated = 0
    
    # Generate log files
    for file_num in range(num_files):
        timestamp = datetime.now() - timedelta(days=num_files - file_num)
        filename = f"ecommerce_app_{timestamp.strftime('%Y%m%d_%H%M%S')}.log"
        filepath = output_path / filename
        
        print(f"\n📝 Generating {filename}...")
        
        with open(filepath, 'w') as f:
            for i in range(logs_per_file):
                # Pick random transaction
                row = df.sample(1).iloc[0]
                
                # Generate timestamp with some randomness
                log_time = timestamp + timedelta(
                    seconds=random.randint(0, 86400),
                    microseconds=random.randint(0, 999999)
                )
                
                # Get log level and generate message
                log_level = get_log_level()
                service, message = generate_log_message(row, log_level)
                
                # Format log line
                log_line = f"{log_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} [{log_level}] [{service}] {message}\n"
                f.write(log_line)
                
                logs_generated += 1
        
        file_size = filepath.stat().st_size / 1024  # KB
        print(f"✓ Generated {logs_per_file:,} logs ({file_size:.1f} KB)")
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"✅ Total log files: {num_files}")
    print(f"✅ Total log entries: {logs_generated:,}")
    print(f"✅ Output directory: {output_path}")
    
    # Show log level distribution
    print(f"\n📊 Log level distribution (configured):")
    for level, prob in LOG_LEVELS.items():
        expected = int(logs_generated * prob)
        print(f"  {level:5s}: ~{expected:,} ({prob*100:.0f}%)")
    
    print(f"\n{'='*60}")
    print("✅ Log generation completed successfully!")
    print('='*60)
    print("\nNext steps:")
    print("  1. Start Flume agent to process logs: bash scripts/start_flume.sh")
    print("  2. Verify logs in HDFS: bash scripts/verify_hdfs.sh")

def main():
    parser = argparse.ArgumentParser(description='Generate application logs from transaction data')
    parser.add_argument('csv_file', nargs='?', help='Source CSV file')
    parser.add_argument('--output-dir', default='logs/incoming', help='Output directory for logs')
    parser.add_argument('--logs-per-file', type=int, default=1000, help='Log entries per file')
    parser.add_argument('--num-files', type=int, default=5, help='Number of log files to generate')
    
    args = parser.parse_args()
    
    # Use default file if not provided
    if not args.csv_file:
        data_dir = Path("/shared-data") if os.path.exists("/shared-data") else Path("shared-data")
        args.csv_file = str(data_dir / "transactions_realtime.csv")
        if not os.path.exists(args.csv_file):
            args.csv_file = str(data_dir / "Online Sales Data.csv")
    
    generate_logs(args.csv_file, args.output_dir, args.logs_per_file, args.num_files)

if __name__ == "__main__":
    main()
