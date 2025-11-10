# Big Data Pipeline Verification Test
# Tests all components: Docker, MySQL, HDFS, Kafka

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "BIG DATA PIPELINE VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$pass = 0
$fail = 0

# Test 1: Containers
Write-Host "[1] Docker Containers..." -ForegroundColor Yellow
$containers = @("mysql", "kafka", "namenode", "datanode", "sqoop", "flume")
$ok = $true
foreach ($c in $containers) {
    $s = docker ps --filter "name=$c" --format "{{.Status}}"
    if ($s -match "Up") {
        Write-Host "  OK: $c" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: $c" -ForegroundColor Red
        $ok = $false
    }
}
if ($ok) { $pass++ } else { $fail++ }

# Test 2: MySQL
Write-Host "`n[2] MySQL Data..." -ForegroundColor Yellow
$count = docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) FROM transactions" -sN 2>$null
if ([int]$count -gt 0) {
    Write-Host "  OK: $count records in MySQL" -ForegroundColor Green
    $pass++
} else {
    Write-Host "  FAIL: No MySQL data" -ForegroundColor Red
    $fail++
}

# Test 3: HDFS
Write-Host "`n[3] HDFS Data..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -test -e /user/sqoop/transactions/part-m-00000.csv 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK: Data in HDFS" -ForegroundColor Green
    $pass++
} else {
    Write-Host "  FAIL: No HDFS data" -ForegroundColor Red
    $fail++
}

# Test 4: Kafka
Write-Host "`n[4] Kafka Topics..." -ForegroundColor Yellow
$topics = docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list 2>$null
if ($topics -match "ecommerce") {
    Write-Host "  OK: Kafka topics found" -ForegroundColor Green
    $pass++
} else {
    Write-Host "  FAIL: No Kafka topics" -ForegroundColor Red
    $fail++
}

# Test 5: Sqoop Available
Write-Host "`n[5] Sqoop Tool..." -ForegroundColor Yellow
$sqoop_version = docker exec sqoop sqoop version 2>$null | Select-String "Sqoop"
if ($sqoop_version) {
    Write-Host "  OK: Sqoop 1.4.7 ready" -ForegroundColor Green
    $pass++
} else {
    Write-Host "  FAIL: Sqoop not available" -ForegroundColor Red
    $fail++
}

# Test 6: Web UI
Write-Host "`n[6] HDFS Web UI..." -ForegroundColor Yellow
try {
    $r = Invoke-WebRequest -Uri "http://localhost:9870" -TimeoutSec 3 -UseBasicParsing
    if ($r.StatusCode -eq 200) {
        Write-Host "  OK: http://localhost:9870" -ForegroundColor Green
        $pass++
    }
} catch {
    Write-Host "  FAIL: Web UI not accessible" -ForegroundColor Red
    $fail++
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RESULTS: $pass passed, $fail failed" -ForegroundColor $(if ($fail -eq 0) { "Green" } else { "Yellow" })
Write-Host "========================================`n" -ForegroundColor Cyan

if ($fail -eq 0) {
    Write-Host "SUCCESS! Pipeline is working!`n" -ForegroundColor Green
    Write-Host "View your data:"
    Write-Host "  Browser: http://localhost:9870`n"
} else {
    Write-Host "Some tests failed. Check above.`n" -ForegroundColor Yellow
}
