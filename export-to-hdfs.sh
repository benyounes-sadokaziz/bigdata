#!/bin/bash

echo "==========================================================="
echo "MySQL to HDFS Export (Python + Docker)"
echo "==========================================================="

# Export data from MySQL to CSV
echo ""
echo "[1/3] Exporting data from MySQL..."
docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT * FROM transactions" --batch > /tmp/mysql_export.csv

echo "✓ Exported $(wc -l < /tmp/mysql_export.csv) lines"

# Copy to namenode
echo ""
echo "[2/3] Copying to HDFS namenode container..."
docker cp /tmp/mysql_export.csv namenode:/tmp/transactions.csv
echo "✓ Copied to namenode:/tmp/transactions.csv"

# Upload to HDFS
echo ""
echo "[3/3] Uploading to HDFS..."
docker exec namenode hdfs dfs -mkdir -p /user/sqoop/transactions
docker exec namenode hdfs dfs -put -f /tmp/transactions.csv /user/sqoop/transactions/part-m-00000.csv

echo "✓ Upload complete!"

# Verify
echo ""
echo "==========================================================="
echo "Verification:"
echo "==========================================================="
docker exec namenode hdfs dfs -ls -R /user/sqoop/

echo ""
echo "Sample Data (first 5 rows):"
docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000.csv | head -6

echo ""
echo "==========================================================="
echo "✓ MySQL→HDFS export completed successfully!"
echo "==========================================================="
