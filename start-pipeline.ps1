# ============================================================================
# Big Data Project - Complete Reset and Step-by-Step Execution
# ============================================================================

Write-Host "`n====================================================================" -ForegroundColor Cyan
Write-Host " BIG DATA PROJECT - RESET & STEP-BY-STEP EXECUTION" -ForegroundColor Cyan
Write-Host "====================================================================`n" -ForegroundColor Cyan

# STEP 0: Clean Up
Write-Host "[STEP 0] CLEAN UP - Removing all existing data`n" -ForegroundColor Green

Write-Host "Cleaning MySQL database..." -ForegroundColor Yellow
docker exec mysql mysql -uroot -prootpassword testdb -e "DELETE FROM transactions;" 2>$null
Write-Host "[OK] MySQL cleared`n" -ForegroundColor Green

Write-Host "Cleaning HDFS..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -rm -r -f /user/sqoop/transactions 2>$null
docker exec namenode hdfs dfs -rm -r -f /user/flume 2>$null
Write-Host "[OK] HDFS cleared`n" -ForegroundColor Green

Write-Host "Recreating Kafka topic..." -ForegroundColor Yellow
docker exec kafka kafka-topics --delete --topic ecommerce-transactions --bootstrap-server localhost:9092 2>$null
Start-Sleep -Seconds 2
docker exec kafka kafka-topics --create --bootstrap-server localhost:9092 --topic ecommerce-transactions --partitions 3 --replication-factor 1 2>$null
Write-Host "[OK] Kafka topic recreated`n" -ForegroundColor Green

Write-Host "[SUCCESS] ALL DATA CLEANED!`n" -ForegroundColor Green
Write-Host "Press Enter to continue..." -ForegroundColor Yellow
Read-Host

# STEP 1: Verify Containers
Write-Host "`n[STEP 1] VERIFY - Checking Docker containers`n" -ForegroundColor Green
docker-compose ps
Write-Host "`nPress Enter to continue..." -ForegroundColor Yellow
Read-Host

# STEP 2: Prepare Dataset
Write-Host "`n[STEP 2] PREPARE - Analyzing and splitting dataset`n" -ForegroundColor Green

Write-Host "Analyzing dataset..." -ForegroundColor Yellow
python scripts/analyze_dataset.py

Write-Host "`nSplitting data (70% historical / 30% real-time)..." -ForegroundColor Yellow
python scripts/split_data.py

Write-Host "`n[SUCCESS] Dataset prepared!`n" -ForegroundColor Green
Write-Host "Press Enter to continue..." -ForegroundColor Yellow
Read-Host

# STEP 3: Load to MySQL
Write-Host "`n[STEP 3] LOAD - Loading historical data to MySQL`n" -ForegroundColor Green

Write-Host "Loading historical transactions..." -ForegroundColor Yellow
python scripts/load_mysql_data.py

Write-Host "`nChecking data in MySQL..." -ForegroundColor Yellow
docker exec mysql mysql -uroot -prootpassword testdb -e "SELECT COUNT(*) as total_records FROM transactions;"
Write-Host ""
docker exec mysql mysql -uroot -prootpassword testdb -e "SELECT * FROM transactions LIMIT 5;"

Write-Host "`n[SUCCESS] Historical data loaded!`n" -ForegroundColor Green
Write-Host "Press Enter to continue..." -ForegroundColor Yellow
Read-Host

# STEP 4: Sqoop Import
Write-Host "`n[STEP 4] SQOOP - Importing MySQL data to HDFS`n" -ForegroundColor Green

Write-Host "Running Sqoop import..." -ForegroundColor Yellow
bash scripts/sqoop_import.sh

Write-Host "`nVerifying data in HDFS..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -ls /user/sqoop/transactions/
Write-Host ""
docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 | Select-Object -First 5

Write-Host "`n[SUCCESS] Sqoop import completed!`n" -ForegroundColor Green
Write-Host "Press Enter to continue..." -ForegroundColor Yellow
Read-Host

# STEP 5: Kafka Setup
Write-Host "`n[STEP 5] KAFKA - Verifying Kafka topics`n" -ForegroundColor Green

Write-Host "Listing Kafka topics..." -ForegroundColor Yellow
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

Write-Host "`nTopic details..." -ForegroundColor Yellow
docker exec kafka kafka-topics --describe --topic ecommerce-transactions --bootstrap-server localhost:9092

Write-Host "`n[SUCCESS] Kafka ready!`n" -ForegroundColor Green
Write-Host "Press Enter to continue..." -ForegroundColor Yellow
Read-Host

# STEP 6: Generate Logs
Write-Host "`n[STEP 6] LOGS - Generating application logs`n" -ForegroundColor Green

Write-Host "Generating sample logs..." -ForegroundColor Yellow
python scripts/generate_logs.py

Write-Host "`nChecking logs directory..." -ForegroundColor Yellow
Get-ChildItem logs/incoming/ | Select-Object Name, Length

Write-Host "`n[SUCCESS] Logs generated!`n" -ForegroundColor Green
Write-Host "Press Enter to continue..." -ForegroundColor Yellow
Read-Host

# STEP 7: Start Flume
Write-Host "`n[STEP 7] FLUME - Starting Flume agents`n" -ForegroundColor Green

Write-Host "Starting Flume agents..." -ForegroundColor Yellow
bash scripts/start_flume.sh

Start-Sleep -Seconds 5

Write-Host "`nChecking Flume processes..." -ForegroundColor Yellow
docker exec flume ps aux | Select-String "flume"

Write-Host "`n[SUCCESS] Flume agents started!`n" -ForegroundColor Green
Write-Host "Press Enter to continue..." -ForegroundColor Yellow
Read-Host

# STEP 8 & 9: Final Instructions
Write-Host "`n====================================================================" -ForegroundColor Cyan
Write-Host " SETUP COMPLETE!" -ForegroundColor Cyan
Write-Host "====================================================================`n" -ForegroundColor Cyan

Write-Host "[OK] Data cleaned and reset" -ForegroundColor Green
Write-Host "[OK] Dataset prepared" -ForegroundColor Green
Write-Host "[OK] Historical data loaded to MySQL" -ForegroundColor Green
Write-Host "[OK] Sqoop import to HDFS completed" -ForegroundColor Green
Write-Host "[OK] Kafka topics ready" -ForegroundColor Green
Write-Host "[OK] Application logs generated" -ForegroundColor Green
Write-Host "[OK] Flume agents running`n" -ForegroundColor Green

Write-Host "====================================================================`n" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host "`n1. Open a NEW PowerShell terminal and run:" -ForegroundColor White
Write-Host "   python scripts/realtime_stream.py" -ForegroundColor Cyan
Write-Host "`n2. Open another NEW PowerShell terminal and run:" -ForegroundColor White
Write-Host "   streamlit run dashboard.py" -ForegroundColor Cyan
Write-Host "`n3. Visit http://localhost:8501" -ForegroundColor White
Write-Host "   Enable 'Auto-refresh' in sidebar to see real-time updates!`n" -ForegroundColor White

Write-Host "====================================================================`n" -ForegroundColor Cyan
Write-Host "Pipeline is ready!" -ForegroundColor Green
Write-Host ""
