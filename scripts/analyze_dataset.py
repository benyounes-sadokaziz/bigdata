#!/usr/bin/env python3
"""
Dataset Analyzer - Phase 1.1
Analyzes the Online Sales Data CSV to understand structure and prepare for processing
"""

import pandas as pd
import os
from pathlib import Path

def analyze_dataset():
    """Analyze the sales dataset and print comprehensive information"""
    
    # Dataset path
    data_dir = Path("/shared-data") if os.path.exists("/shared-data") else Path("shared-data")
    csv_file = data_dir / "Online Sales Data.csv"
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║          E-Commerce Dataset Analysis Report                ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Check if file exists
    if not csv_file.exists():
        print(f"❌ Error: File not found at {csv_file}")
        return
    
    # Get file size
    file_size_mb = csv_file.stat().st_size / (1024 * 1024)
    print(f"📁 File: {csv_file.name}")
    print(f"📊 Size: {file_size_mb:.2f} MB\n")
    
    # Read the dataset
    print("📖 Loading dataset...")
    df = pd.read_csv(csv_file)
    
    # Basic statistics
    print(f"\n{'='*60}")
    print("BASIC STATISTICS")
    print('='*60)
    print(f"Total Rows: {len(df):,}")
    print(f"Total Columns: {len(df.columns)}")
    print(f"\nColumn Names and Types:")
    print("-" * 60)
    for col in df.columns:
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        print(f"  {col:30s} | {str(dtype):12s} | {null_count} nulls")
    
    # Sample data
    print(f"\n{'='*60}")
    print("SAMPLE DATA (First 5 rows)")
    print('='*60)
    print(df.head().to_string())
    
    # Value counts for categorical columns
    print(f"\n{'='*60}")
    print("CATEGORICAL DATA ANALYSIS")
    print('='*60)
    
    categorical_cols = ['Product Category', 'Region', 'Payment Method']
    for col in categorical_cols:
        if col in df.columns:
            print(f"\n{col}:")
            print(df[col].value_counts())
    
    # Numerical statistics
    print(f"\n{'='*60}")
    print("NUMERICAL DATA STATISTICS")
    print('='*60)
    numerical_cols = ['Units Sold', 'Unit Price', 'Total Revenue']
    if all(col in df.columns for col in numerical_cols):
        print(df[numerical_cols].describe())
    
    # Date analysis
    print(f"\n{'='*60}")
    print("DATE ANALYSIS")
    print('='*60)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        print(f"Date Range: {df['Date'].min()} to {df['Date'].max()}")
        print(f"Total Days: {(df['Date'].max() - df['Date'].min()).days}")
        print(f"\nTransactions by Month:")
        print(df.groupby(df['Date'].dt.to_period('M')).size())
    
    # Recommendations
    print(f"\n{'='*60}")
    print("RECOMMENDED DATA SPLIT STRATEGY")
    print('='*60)
    total_rows = len(df)
    historical_count = int(total_rows * 0.7)
    realtime_count = total_rows - historical_count
    
    print(f"\nTotal Records: {total_rows:,}")
    print(f"  ├─ Historical (MySQL): {historical_count:,} records (70%)")
    print(f"  └─ Real-time (Kafka):  {realtime_count:,} records (30%)\n")
    
    if 'Date' in df.columns:
        split_date = df.sort_values('Date').iloc[historical_count]['Date']
        print(f"Suggested Split Date: {split_date}")
        print(f"  ├─ Historical: Before {split_date}")
        print(f"  └─ Real-time: From {split_date} onwards")
    
    print(f"\n{'='*60}")
    print("COMPONENT MAPPING")
    print('='*60)
    print("✓ MySQL (Historical Data):")
    print("  └─ First 70% of transactions")
    print("\n✓ Kafka (Real-time Stream):")
    print("  └─ Last 30% of transactions (streamed slowly)")
    print("\n✓ Logs (Application Logs):")
    print("  └─ Generated from real-time transactions")
    
    print("\n✅ Analysis Complete!\n")

if __name__ == "__main__":
    analyze_dataset()
