# ============================================================================
# Big Data Project - Complete Reset and Step-by-Step Execution
# ============================================================================

Write-Host "`n============================================================================" -ForegroundColor Cyan
Write-Host "BIG DATA PROJECT - COMPLETE RESET & STEP-BY-STEP EXECUTION" -ForegroundColor Cyan
Write-Host "============================================================================`n" -ForegroundColor Cyan

# Function to wait for user
function Wait-ForUser {
    param([string]$message = "Press Enter to continue...")
    Write-Host "`n$message" -ForegroundColor Yellow
    Read-Host
}

# Function to run step
function Run-Step {
    param(
        [string]$stepNumber,
        [string]$description,
        [scriptblock]$action
    )
    Write-Host "`n============================================================================" -ForegroundColor Green
    Write-Host "STEP $stepNumber : $description" -ForegroundColor Green
    Write-Host "============================================================================" -ForegroundColor Green
    & $action
}

# ============================================================================
# STEP 0: Clean Up Existing Data
# ============================================================================
Run-Step "0" "CLEAN UP - Removing all existing data" {
    Write-Host "`nCleaning MySQL database..." -ForegroundColor Yellow
    docker exec mysql mysql -uroot -prootpassword testdb -e "DELETE FROM transactions;" 2>&1 | Out-Null
    Write-Host "✓ MySQL cleared" -ForegroundColor Green
    
    Write-Host "`nCleaning HDFS..." -ForegroundColor Yellow
    docker exec namenode hdfs dfs -rm -r -f /user/sqoop/transactions 2>&1 | Out-Null
    docker exec namenode hdfs dfs -rm -r -f /user/flume 2>&1 | Out-Null
    Write-Host "✓ HDFS cleared" -ForegroundColor Green
    
    Write-Host "`nRecreating Kafka topic..." -ForegroundColor Yellow
    docker exec kafka kafka-topics --delete --topic ecommerce-transactions --bootstrap-server localhost:9092 2>&1 | Out-Null
    Start-Sleep -Seconds 2
    docker exec kafka kafka-topics --create --bootstrap-server localhost:9092 --topic ecommerce-transactions --partitions 3 --replication-factor 1 2>&1 | Out-Null
    Write-Host "✓ Kafka topic recreated" -ForegroundColor Green
    
    Write-Host "`n✅ ALL DATA CLEANED!" -ForegroundColor Green
}

Wait-ForUser

# ============================================================================
# STEP 1: Verify Docker Containers
# ============================================================================
Run-Step "1" "VERIFY - Checking all Docker containers are running" {
    Write-Host ""
    docker-compose ps
    Write-Host "`n✅ All containers should show 'Up' status" -ForegroundColor Green
}

Wait-ForUser

# ============================================================================
# STEP 2: Prepare Dataset
# ============================================================================
Run-Step "2" "PREPARE - Analyzing and splitting dataset" {
    Write-Host "`n📊 Analyzing dataset..." -ForegroundColor Yellow
    python scripts/analyze_dataset.py
    
    Write-Host "`n✂️ Splitting data (70% historical / 30% real-time)..." -ForegroundColor Yellow
    python scripts/split_data.py
    
    Write-Host "`n✅ Dataset prepared!" -ForegroundColor Green
}

Wait-ForUser

# ============================================================================
# STEP 3: Load Historical Data to MySQL
# ============================================================================
Run-Step "3" "LOAD - Loading historical data to MySQL" {
    Write-Host "`n[INFO] Loading historical transactions to MySQL..." -ForegroundColor Yellow
    python scripts/load_mysql_data.py
    
    Write-Host "`n[INFO] Checking data in MySQL..." -ForegroundColor Yellow
    docker exec mysql mysql -uroot -prootpassword testdb -e "SELECT COUNT(*) as total_records FROM transactions;"
    docker exec mysql mysql -uroot -prootpassword testdb -e "SELECT * FROM transactions LIMIT 5;" 
    
    Write-Host "`n[SUCCESS] Historical data loaded to MySQL!" -ForegroundColor Green
}

Wait-ForUser

# ============================================================================
# STEP 4: Import MySQL Data to HDFS via Sqoop
# ============================================================================
Run-Step "4" "SQOOP - Importing MySQL data to HDFS" {
    Write-Host "`n🔄 Running Sqoop import..." -ForegroundColor Yellow
    bash scripts/sqoop_import.sh
    
    Write-Host "`n📂 Verifying data in HDFS..." -ForegroundColor Yellow
    docker exec namenode hdfs dfs -ls /user/sqoop/transactions/
    docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 | Select-Object -First 5
    
    Write-Host "`n✅ Sqoop import completed!" -ForegroundColor Green
}

Wait-ForUser

# ============================================================================
# STEP 5: Setup Kafka Topics
# ============================================================================
Run-Step "5" "KAFKA - Verifying Kafka setup" {
    Write-Host "`n📋 Listing Kafka topics..." -ForegroundColor Yellow
    docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
    
    Write-Host "`n📝 Topic details..." -ForegroundColor Yellow
    docker exec kafka kafka-topics --describe --topic ecommerce-transactions --bootstrap-server localhost:9092
    
    Write-Host "`n✅ Kafka ready!" -ForegroundColor Green
}

Wait-ForUser

# ============================================================================
# STEP 6: Generate Application Logs
# ============================================================================
Run-Step "6" "LOGS - Generating application logs" {
    Write-Host "`n📝 Generating sample logs..." -ForegroundColor Yellow
    python scripts/generate_logs.py
    
    Write-Host "`n📂 Checking logs directory..." -ForegroundColor Yellow
    Get-ChildItem logs/incoming/ | Select-Object Name, Length
    
    Write-Host "`n✅ Logs generated!" -ForegroundColor Green
}

Wait-ForUser

# ============================================================================
# STEP 7: Start Flume Agents
# ============================================================================
Run-Step "7" "FLUME - Starting Flume agents" {
    Write-Host "`n🌊 Starting Flume agents..." -ForegroundColor Yellow
    bash scripts/start_flume.sh
    
    Start-Sleep -Seconds 5
    
    Write-Host "`n📊 Checking Flume processes..." -ForegroundColor Yellow
    docker exec flume ps aux | Select-String "flume"
    
    Write-Host "`n✅ Flume agents started!" -ForegroundColor Green
}

Wait-ForUser

# ============================================================================
# STEP 8: Start Real-time Streaming
# ============================================================================
Run-Step "8" "STREAMING - Ready to start real-time data streaming" {
    Write-Host "`n🚀 To start real-time streaming, open a NEW terminal and run:" -ForegroundColor Yellow
    Write-Host "`n   python scripts/realtime_stream.py`n" -ForegroundColor Cyan
    Write-Host "This will:" -ForegroundColor White
    Write-Host "  • Generate new transactions every 3 seconds" -ForegroundColor White
    Write-Host "  • Send to Kafka topic: ecommerce-transactions" -ForegroundColor White
    Write-Host "  • Save to MySQL database: testdb.transactions" -ForegroundColor White
    Write-Host "  • Flume will consume from Kafka and write to HDFS" -ForegroundColor White
    
    Write-Host "`n✅ Pipeline ready for real-time streaming!" -ForegroundColor Green
}

Wait-ForUser

# ============================================================================
# STEP 9: Launch Dashboard
# ============================================================================
Run-Step "9" "DASHBOARD - Launching Streamlit dashboard" {
    Write-Host "`n📊 To launch the dashboard, open a NEW terminal and run:" -ForegroundColor Yellow
    Write-Host "`n   streamlit run dashboard.py`n" -ForegroundColor Cyan
    Write-Host "Dashboard will be available at: http://localhost:8501" -ForegroundColor White
    Write-Host "`nEnable 'Auto-refresh' in the sidebar to see real-time updates!" -ForegroundColor White
    
    Write-Host "`n✅ Ready to visualize!" -ForegroundColor Green
}

Wait-ForUser

# ============================================================================
# FINAL SUMMARY
# ============================================================================
Write-Host "`n============================================================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE - SUMMARY" -ForegroundColor Cyan
Write-Host "============================================================================`n" -ForegroundColor Cyan

Write-Host "✅ Data cleaned and reset" -ForegroundColor Green
Write-Host "✅ Dataset prepared (historical/realtime split)" -ForegroundColor Green
Write-Host "✅ Historical data loaded to MySQL" -ForegroundColor Green
Write-Host "✅ Sqoop import to HDFS completed" -ForegroundColor Green
Write-Host "✅ Kafka topics ready" -ForegroundColor Green
Write-Host "✅ Application logs generated" -ForegroundColor Green
Write-Host "✅ Flume agents running" -ForegroundColor Green

Write-Host "`n📋 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "   1. Open a NEW terminal:" -ForegroundColor White
Write-Host "      python scripts/realtime_stream.py" -ForegroundColor Cyan
Write-Host "`n   2. Open another NEW terminal:" -ForegroundColor White
Write-Host "      streamlit run dashboard.py" -ForegroundColor Cyan
Write-Host "`n   3. Visit http://localhost:8501 and enable auto-refresh`n" -ForegroundColor White

Write-Host "============================================================================`n" -ForegroundColor Cyan

Write-Host "🎉 Your Big Data pipeline is ready!" -ForegroundColor Green
Write-Host ""
