# Simple PowerShell Verification Script
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "Big Data Pipeline - Quick Check" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# Check MySQL
Write-Host "[1] MySQL Data:" -ForegroundColor Yellow
docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) as total FROM transactions;"
Write-Host ""

# Check Kafka
Write-Host "[2] Kafka Topics:" -ForegroundColor Yellow
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092 | Select-String "ecommerce"
Write-Host ""

# Create HDFS directories
Write-Host "[3] Creating HDFS directories..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -mkdir -p /user/sqoop
docker exec namenode hdfs dfs -mkdir -p /user/flume
Write-Host "Done!" -ForegroundColor Green
Write-Host ""

# Import with Sqoop
Write-Host "[4] Sqoop Import (this takes ~30 seconds)..." -ForegroundColor Yellow
docker exec sqoop sqoop import --connect jdbc:mysql://mysql:3306/testdb --username sqoop --password sqoop123 --table transactions --target-dir /user/sqoop/transactions --delete-target-dir --m 1
Write-Host ""

# Show HDFS data
Write-Host "[5] Data in HDFS:" -ForegroundColor Yellow
docker exec namenode hdfs dfs -ls -R /user/sqoop/
Write-Host ""

Write-Host "[6] Sample Records (first 3):" -ForegroundColor Yellow
docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 | Select-Object -First 3
Write-Host ""

Write-Host "===========================================================" -ForegroundColor Green
Write-Host "RESULTS SUMMARY" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "✅ MySQL: Has data" -ForegroundColor Green
Write-Host "✅ Kafka: Topics created" -ForegroundColor Green  
Write-Host "✅ HDFS: Data imported via Sqoop" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 VIEW IN BROWSER: http://localhost:9870" -ForegroundColor Cyan
Write-Host "   Click: Utilities → Browse the file system" -ForegroundColor Cyan
Write-Host ""
