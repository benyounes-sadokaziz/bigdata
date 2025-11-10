# ============================================================
# Big Data Pipeline - Complete Launch Script
# Starts all components in the correct order
# ============================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     BIG DATA PIPELINE - COMPLETE STARTUP                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Step 1: Start Docker Containers
Write-Host "[1/5] Starting Docker Containers..." -ForegroundColor Yellow
Write-Host "  This may take 1-2 minutes on first run..." -ForegroundColor Gray

docker-compose up -d

Write-Host "  ✓ Containers starting..." -ForegroundColor Green
Write-Host ""

# Step 2: Wait for services
Write-Host "[2/5] Waiting for services to be ready..." -ForegroundColor Yellow
Write-Host "  Waiting 30 seconds for MySQL, Kafka, and HDFS to initialize..." -ForegroundColor Gray

Start-Sleep -Seconds 30

Write-Host "  ✓ Services should be ready" -ForegroundColor Green
Write-Host ""

# Step 3: Verify containers
Write-Host "[3/5] Verifying container status..." -ForegroundColor Yellow

$containers = @("mysql", "kafka", "zookeeper", "namenode", "datanode", "sqoop", "flume")
$all_running = $true

foreach ($container in $containers) {
    $status = docker ps --filter "name=$container" --format "{{.Status}}"
    if ($status -match "Up") {
        Write-Host "  ✓ $container is running" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $container is NOT running" -ForegroundColor Red
        $all_running = $false
    }
}

if (-not $all_running) {
    Write-Host ""
    Write-Host "⚠ Warning: Some containers are not running!" -ForegroundColor Yellow
    Write-Host "  You may need to wait longer or check logs:" -ForegroundColor Yellow
    Write-Host "  docker logs mysql" -ForegroundColor Gray
    Write-Host ""
}

Write-Host ""

# Step 4: Check if data exists
Write-Host "[4/5] Checking data status..." -ForegroundColor Yellow

$mysql_count = docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) FROM transactions" -sN 2>$null
if ([int]$mysql_count -gt 0) {
    Write-Host "  ✓ MySQL has $mysql_count records" -ForegroundColor Green
} else {
    Write-Host "  ⚠ MySQL has no data - run pipeline to load data" -ForegroundColor Yellow
}

docker exec namenode hdfs dfs -test -e /user/sqoop/transactions/part-m-00000.csv 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ HDFS has data files" -ForegroundColor Green
} else {
    Write-Host "  ⚠ HDFS has no data - run pipeline to load data" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Launch Dashboard
Write-Host "[5/5] Launching Dashboard..." -ForegroundColor Yellow

Write-Host "  Starting Streamlit dashboard..." -ForegroundColor Gray
Write-Host ""

# Start dashboard in background
Start-Process powershell -ArgumentList "-NoExit", "-Command", "streamlit run dashboard.py --server.port 8501"

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              🎉 LAUNCH COMPLETE!                          ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "🌐 Access Points:" -ForegroundColor Cyan
Write-Host "  ┌────────────────────────────────────────────────────────┐"
Write-Host "  │  📊 Dashboard:  http://localhost:8501                 │" -ForegroundColor Magenta
Write-Host "  │  💾 HDFS UI:    http://localhost:9870                 │" -ForegroundColor Magenta
Write-Host "  └────────────────────────────────────────────────────────┘"
Write-Host ""

Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  If this is your first time running:" -ForegroundColor Cyan
Write-Host "    1. Load data into the pipeline:"
Write-Host "       python run-full-pipeline.py"
Write-Host ""
Write-Host "  Test the pipeline:" -ForegroundColor Cyan
Write-Host "    .\test-pipeline.ps1"
Write-Host ""
Write-Host "  View your dashboard:" -ForegroundColor Cyan
Write-Host "    Open browser → http://localhost:8501"
Write-Host ""

Write-Host "🛑 To Stop Everything:" -ForegroundColor Yellow
Write-Host "  docker-compose down"
Write-Host "  (Close the dashboard PowerShell window)"
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
