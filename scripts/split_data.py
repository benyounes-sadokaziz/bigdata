#!/usr/bin/env python3
"""
Data Splitter - Phase 1.2
Splits Online Sales Data into historical (MySQL) and real-time (Kafka) portions
"""

import pandas as pd
import os
from pathlib import Path

def split_data(split_ratio=0.7):
    """
    Split the sales data into historical and real-time portions
    
    Args:
        split_ratio: Percentage of data for historical (default 0.7 for 70%)
    """
    
    # Dataset paths
    data_dir = Path("/shared-data") if os.path.exists("/shared-data") else Path("shared-data")
    input_file = data_dir / "Online Sales Data.csv"
    
    output_historical = data_dir / "transactions_historical.csv"
    output_realtime = data_dir / "transactions_realtime.csv"
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║              Data Splitting Process                        ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Check if file exists
    if not input_file.exists():
        print(f"❌ Error: Input file not found at {input_file}")
        return
    
    # Read the dataset
    print(f"📖 Loading dataset from {input_file.name}...")
    df = pd.read_csv(input_file)
    print(f"✓ Loaded {len(df):,} records\n")
    
    # Convert date column to datetime for proper sorting
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        # Sort by date to split chronologically
        df = df.sort_values('Date').reset_index(drop=True)
        print("✓ Data sorted by date")
    
    # Calculate split point
    total_rows = len(df)
    split_point = int(total_rows * split_ratio)
    
    # Split the data
    df_historical = df.iloc[:split_point].copy()
    df_realtime = df.iloc[split_point:].copy()
    
    print(f"\n{'='*60}")
    print("SPLIT SUMMARY")
    print('='*60)
    print(f"Total Records:      {total_rows:,}")
    print(f"Historical (MySQL): {len(df_historical):,} records ({split_ratio*100:.0f}%)")
    print(f"Real-time (Kafka):  {len(df_realtime):,} records ({(1-split_ratio)*100:.0f}%)")
    
    if 'Date' in df.columns:
        print(f"\nDate Ranges:")
        print(f"Historical: {df_historical['Date'].min()} to {df_historical['Date'].max()}")
        print(f"Real-time:  {df_realtime['Date'].min()} to {df_realtime['Date'].max()}")
    
    # Save the split files
    print(f"\n{'='*60}")
    print("SAVING FILES")
    print('='*60)
    
    print(f"💾 Saving historical data to {output_historical.name}...")
    df_historical.to_csv(output_historical, index=False)
    print(f"✓ Saved {len(df_historical):,} records")
    
    print(f"\n💾 Saving real-time data to {output_realtime.name}...")
    df_realtime.to_csv(output_realtime, index=False)
    print(f"✓ Saved {len(df_realtime):,} records")
    
    # Verify files
    print(f"\n{'='*60}")
    print("VERIFICATION")
    print('='*60)
    verify_historical = pd.read_csv(output_historical)
    verify_realtime = pd.read_csv(output_realtime)
    print(f"✓ Historical file verified: {len(verify_historical):,} records")
    print(f"✓ Real-time file verified:  {len(verify_realtime):,} records")
    print(f"✓ Total matches original:  {len(verify_historical) + len(verify_realtime) == total_rows}")
    
    print("\n✅ Data splitting completed successfully!\n")
    print("Next steps:")
    print("  1. Run generate_mysql_schema.py to create SQL schema")
    print("  2. Run load_mysql_data.py to load historical data to MySQL")

if __name__ == "__main__":
    split_data()
