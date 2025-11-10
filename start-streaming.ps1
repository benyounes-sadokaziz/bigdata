# Start Real-time Data Streaming
# This script starts the real-time data generator in the background

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "   REAL-TIME DATA STREAMING - Big Data Pipeline" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if containers are running
Write-Host "[1/3] Checking Docker containers..." -ForegroundColor Yellow
$containers = docker ps --format "{{.Names}}" 2>$null

if ($containers -notcontains "kafka" -or $containers -notcontains "mysql") {
    Write-Host "❌ Error: Kafka or MySQL containers are not running" -ForegroundColor Red
    Write-Host "Please start containers first: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Docker containers are running" -ForegroundColor Green
Write-Host ""

# Check if dashboard is running
Write-Host "[2/3] Checking Streamlit dashboard..." -ForegroundColor Yellow
$streamlitProcess = Get-Process -Name streamlit -ErrorAction SilentlyContinue
if ($streamlitProcess) {
    Write-Host "✅ Streamlit dashboard is running on http://localhost:8501" -ForegroundColor Green
} else {
    Write-Host "⚠️  Streamlit dashboard is not running" -ForegroundColor Yellow
    Write-Host "   Start it with: streamlit run dashboard.py" -ForegroundColor Yellow
}
Write-Host ""

# Start real-time streaming
Write-Host "[3/3] Starting real-time data streaming..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  • Interval: 3 seconds per transaction" -ForegroundColor White
Write-Host "  • Target: Kafka + MySQL" -ForegroundColor White
Write-Host "  • Dashboard auto-refresh: Enable in sidebar" -ForegroundColor White
Write-Host ""
Write-Host "Instructions:" -ForegroundColor Cyan
Write-Host "  1. Open dashboard: http://localhost:8501" -ForegroundColor White
Write-Host "  2. Enable 'Auto-refresh' in sidebar" -ForegroundColor White
Write-Host "  3. Set refresh interval (5-10 seconds recommended)" -ForegroundColor White
Write-Host "  4. Watch real-time updates in Overview and Sales Analytics" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop streaming" -ForegroundColor Yellow
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Wait a moment
Start-Sleep -Seconds 2

# Run the streaming script
python scripts/realtime_stream.py
