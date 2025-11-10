# Big Data Pipeline Dashboard Launcher
# Start the Streamlit dashboard

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Big Data Dashboard" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Dashboard will open in your browser..." -ForegroundColor Green
Write-Host "URL: http://localhost:8501" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the dashboard" -ForegroundColor Yellow
Write-Host ""

# Start Streamlit
streamlit run dashboard.py --server.port 8501 --server.address localhost
