# Reset and Run Complete Real-time Pipeline
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "   RESET & RUN - Real-time Big Data Pipeline" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clear existing data
Write-Host "[1/6] Clearing existing data..." -ForegroundColor Yellow
docker exec mysql mysql -uroot -prootpassword -e "DROP DATABASE IF EXISTS ecommerce;" 2>$null
docker exec mysql mysql -uroot -prootpassword -e "CREATE DATABASE ecommerce;" 2>$null
docker exec mysql mysql -uroot -prootpassword ecommerce -e "CREATE TABLE transactions (transaction_id INT PRIMARY KEY, product_name VARCHAR(255), category VARCHAR(100), quantity INT, unit_price DECIMAL(10,2), total_amount DECIMAL(10,2), payment_method VARCHAR(50), region VARCHAR(50), timestamp DATETIME);" 2>$null
docker exec namenode hdfs dfs -rm -r -f /user/sqoop/transactions 2>$null
docker exec namenode hdfs dfs -rm -r -f /user/flume 2>$null
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic ecommerce-transactions 2>$null
Start-Sleep -Seconds 2
docker exec kafka kafka-topics --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 3 --topic ecommerce-transactions 2>$null
Write-Host "  DONE!" -ForegroundColor Green
Write-Host ""

# Step 2: Load seed data
Write-Host "[2/6] Loading 10 seed transactions..." -ForegroundColor Yellow
docker exec mysql mysql -uroot -prootpassword ecommerce -e "INSERT INTO transactions VALUES (1, 'Laptop', 'Electronics', 1, 999.99, 999.99, 'Credit Card', 'North', NOW());" 2>$null
docker exec mysql mysql -uroot -prootpassword ecommerce -e "INSERT INTO transactions VALUES (2, 'T-Shirt', 'Clothing', 3, 25.00, 75.00, 'Debit Card', 'South', NOW());" 2>$null
docker exec mysql mysql -uroot -prootpassword ecommerce -e "INSERT INTO transactions VALUES (3, 'Coffee Maker', 'Home', 1, 79.99, 79.99, 'PayPal', 'East', NOW());" 2>$null
docker exec mysql mysql -uroot -prootpassword ecommerce -e "INSERT INTO transactions VALUES (4, 'Smartphone', 'Electronics', 2, 699.99, 1399.98, 'Credit Card', 'West', NOW());" 2>$null
docker exec mysql mysql -uroot -prootpassword ecommerce -e "INSERT INTO transactions VALUES (5, 'Book', 'Books', 5, 15.99, 79.95, 'Cash', 'Central', NOW());" 2>$null
docker exec mysql mysql -uroot -prootpassword ecommerce -e "INSERT INTO transactions VALUES (6, 'Headphones', 'Electronics', 1, 149.99, 149.99, 'Credit Card', 'North', NOW());" 2>$null
docker exec mysql mysql -uroot -prootpassword ecommerce -e "INSERT INTO transactions VALUES (7, 'Jeans', 'Clothing', 2, 59.99, 119.98, 'Debit Card', 'South', NOW());" 2>$null
docker exec mysql mysql -uroot -prootpassword ecommerce -e "INSERT INTO transactions VALUES (8, 'Blender', 'Home', 1, 89.99, 89.99, 'PayPal', 'East', NOW());" 2>$null
docker exec mysql mysql -uroot -prootpassword ecommerce -e "INSERT INTO transactions VALUES (9, 'Desk Lamp', 'Home', 1, 34.99, 34.99, 'Cash', 'West', NOW());" 2>$null
docker exec mysql mysql -uroot -prootpassword ecommerce -e "INSERT INTO transactions VALUES (10, 'Sneakers', 'Clothing', 1, 119.99, 119.99, 'Credit Card', 'Central', NOW());" 2>$null
Write-Host "  DONE!" -ForegroundColor Green
Write-Host ""

# Step 3: Check Streamlit
Write-Host "[3/6] Checking Streamlit dashboard..." -ForegroundColor Yellow
$streamlitProcess = Get-Process -Name streamlit -ErrorAction SilentlyContinue
if ($streamlitProcess) {
    Write-Host "  Streamlit is running at http://localhost:8501" -ForegroundColor Green
} else {
    Write-Host "  Starting Streamlit dashboard..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit -Command streamlit run dashboard.py --server.port 8501"
    Start-Sleep -Seconds 5
    Write-Host "  Dashboard started!" -ForegroundColor Green
}
Write-Host ""

# Step 4: Show status
Write-Host "[4/6] Current system status..." -ForegroundColor Yellow
$count = docker exec mysql mysql -uroot -prootpassword ecommerce -e "SELECT COUNT(*) FROM transactions;" 2>$null | Select-Object -Last 1
Write-Host "  Transactions in database: $count" -ForegroundColor Cyan
Write-Host "  Dashboard URL: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""

# Step 5: Instructions
Write-Host "[5/6] INSTRUCTIONS FOR REAL-TIME UPDATES:" -ForegroundColor Yellow
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host "1. Open browser: http://localhost:8501" -ForegroundColor White
Write-Host "2. In Streamlit sidebar: Enable 'Auto-refresh' (5-10 seconds)" -ForegroundColor White
Write-Host "3. Press ENTER below to start streaming new transactions" -ForegroundColor White
Write-Host "==========================================================================" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press ENTER when Auto-refresh is enabled in dashboard"

# Step 6: Start streaming
Write-Host ""
Write-Host "[6/6] STARTING REAL-TIME STREAMING..." -ForegroundColor Green
Write-Host "  Generating 1 transaction every 3 seconds" -ForegroundColor Yellow
Write-Host "  Watch your dashboard update in real-time!" -ForegroundColor Cyan
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Red
Write-Host ""
Start-Sleep -Seconds 2
python scripts/realtime_stream.py
