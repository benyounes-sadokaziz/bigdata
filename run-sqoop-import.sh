#!/bin/bash

echo "Starting Sqoop import from MySQL to HDFS..."

# Run Sqoop import with proper classpath
docker exec sqoop bash -c "sqoop import \
  --connect jdbc:mysql://mysql:3306/testdb \
  --username sqoop \
  --password sqoop123 \
  --table transactions \
  --target-dir /user/sqoop/transactions \
  --delete-target-dir \
  --fields-terminated-by ',' \
  --lines-terminated-by '\n' \
  --num-mappers 1 \
  --verbose"

echo ""
echo "Verifying imported data in HDFS..."
docker exec namenode hdfs dfs -ls -R /user/sqoop/

echo ""
echo "Sample of imported data:"
docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 | head -5
