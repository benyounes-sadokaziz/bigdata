# 🔴 REAL-TIME DASHBOARD GUIDE

## Quick Start - See Live Updates in 3 Steps

### Step 1: Start All Services
```powershell
# Start Docker containers
docker-compose up -d

# Wait 10 seconds for services to initialize
Start-Sleep -Seconds 10
```

### Step 2: Launch Dashboard
```powershell
# Start Streamlit dashboard in a new terminal
streamlit run dashboard.py --server.port 8501
```

The dashboard will open automatically at: **http://localhost:8501**

### Step 3: Start Real-time Data Streaming
```powershell
# In a NEW terminal, run:
.\start-streaming.ps1
```

This will:
- ✅ Generate new transactions every 3 seconds
- ✅ Send data to Kafka + MySQL simultaneously
- ✅ Enable real-time dashboard updates

---

## 🎛️ Dashboard Controls for Real-time Updates

### In the Streamlit Sidebar:

1. **Enable Auto-refresh**
   - ✅ Check the "Auto-refresh" checkbox
   
2. **Set Refresh Interval**
   - 🎚️ Use the slider: **5-10 seconds recommended**
   - Lower = more frequent updates (uses more resources)
   - Higher = less frequent updates (more stable)

3. **Watch the Live Indicator**
   - 🟢 Green blinking dot = Real-time mode active
   - Last update time shown below controls

---

## 📊 What You'll See in Real-time

### Overview Page
- **Live Transaction Feed**: Latest 10 transactions
- **Real-time Metrics**: Total transactions, revenue, average
- **Dynamic Charts**: Revenue by category, sales by region

### Sales Analytics Page  
- **Live Updates Indicator**: Green dot when auto-refresh enabled
- **Revenue Trend**: Updates as new transactions arrive
- **Top Products**: Rankings change in real-time

### Pipeline Status Page
- **Container Health**: Real-time status of all services
- **HDFS Usage**: Live storage metrics

---

## 🚀 Full Launch Command (All-in-One)

Run this to start everything:

```powershell
# Terminal 1: Start services and dashboard
docker-compose up -d; Start-Sleep -Seconds 10; streamlit run dashboard.py

# Terminal 2: Start real-time streaming
.\start-streaming.ps1
```

---

## 🎯 Recommended Settings

| Setting | Value | Why |
|---------|-------|-----|
| **Refresh Interval** | 5-10 seconds | Balance between updates and performance |
| **Transaction Rate** | 3 seconds | Smooth flow without overwhelming system |
| **Dashboard Page** | Overview | Best for watching live transactions |

---

## 📈 What to Watch

1. **Transaction Counter** - Increases with each new transaction
2. **Total Revenue** - Grows in real-time
3. **Live Transaction Feed** - New entries appear at the top
4. **Category Charts** - Bars grow as products are sold
5. **Regional Distribution** - Pie chart updates with new sales

---

## ⚡ Performance Tips

### For Smooth Real-time Experience:

1. **Close Unnecessary Tabs**
   - Keep only the dashboard open in browser
   
2. **Optimal Refresh Rate**
   - Start with 10 seconds
   - Decrease if your system handles it well
   
3. **Monitor System Resources**
   - Watch CPU/Memory in Task Manager
   - Increase refresh interval if system slows down

4. **Kafka Consumer Lag**
   - Check Kafka UI: http://localhost:8080
   - Ensure no lag in ecommerce-transactions topic

---

## 🛑 How to Stop Everything

```powershell
# Stop data streaming: Press Ctrl+C in streaming terminal

# Stop dashboard: Press Ctrl+C in dashboard terminal

# Stop Docker containers:
docker-compose down
```

---

## 🔍 Troubleshooting Real-time Issues

### Dashboard Not Updating?

**Check 1**: Is auto-refresh enabled?
- Look for ✅ checkbox in sidebar

**Check 2**: Is streaming script running?
- You should see "Sent to Kafka" messages every 3 seconds

**Check 3**: Are containers healthy?
```powershell
docker ps  # All should show "Up" status
```

### No New Transactions Appearing?

**Check 1**: Verify Kafka connection
```powershell
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
# Should show: ecommerce-transactions
```

**Check 2**: Verify MySQL data
```powershell
docker exec mysql mysql -uroot -prootpassword -e "SELECT COUNT(*) FROM ecommerce.transactions;"
```

**Check 3**: Check streaming script logs
- Should show: "✅ Transaction #XXX processed successfully"

### Dashboard Loads Slowly?

**Solution 1**: Increase refresh interval
- Move slider to 15-20 seconds

**Solution 2**: Reduce transaction rate
- Edit `start-streaming.ps1`, change `interval=3` to `interval=5`

**Solution 3**: Clear cache
- Click "🔄 Refresh Now" button in sidebar

---

## 📊 Expected Behavior

### After 1 Minute of Streaming:
- ~20 new transactions
- Revenue increased by $500-$2000
- 3-5 new entries in transaction feed

### After 5 Minutes:
- ~100 new transactions  
- Multiple category updates
- Regional distribution changes visible

### After 10 Minutes:
- ~200 new transactions
- Clear trends in revenue chart
- Top products ranking may shift

---

## 🎨 Dashboard Pages Explained

### 1️⃣ Overview (Best for Real-time)
- System health metrics
- Live transaction feed (top 10)
- Real-time revenue counters
- Category and region charts

### 2️⃣ Sales Analytics
- Revenue trends over time
- Top 10 products
- Category performance
- Payment method distribution

### 3️⃣ Pipeline Status
- Docker container health
- HDFS storage metrics
- Kafka topic information
- System architecture diagram

### 4️⃣ Data Explorer
- Browse all transactions
- Filter by date, category, region
- Export to CSV
- Detailed transaction search

---

## ✨ Advanced: Customize Streaming Rate

Edit `scripts/realtime_stream.py`:

```python
# Line 223: Change interval (seconds between transactions)
streamer.stream_data(interval=3, duration=None)

# Examples:
interval=1   # Fast: 1 transaction/second (demo mode)
interval=3   # Default: 1 transaction/3 seconds (recommended)
interval=5   # Slow: 1 transaction/5 seconds (stable)
```

---

## 📱 Access Dashboard from Another Device

If you want to view the dashboard from your phone/tablet:

1. Find your computer's IP address:
```powershell
ipconfig | findstr IPv4
# Example: 192.168.1.100
```

2. Start dashboard with network access:
```powershell
streamlit run dashboard.py --server.port 8501 --server.address 0.0.0.0
```

3. Open on other device:
```
http://YOUR_IP:8501
# Example: http://192.168.1.100:8501
```

---

## 🎓 Understanding the Data Flow

```
Real-time Data Streaming Script
            ↓
    [Generate Transaction]
            ↓
    ┌───────┴───────┐
    ↓               ↓
[Kafka Topic]   [MySQL DB]
    ↓               ↓
[Flume Agent]  [Dashboard Query]
    ↓               ↓
[HDFS Storage] [Streamlit UI]
                    ↓
            [Your Browser]
                (Updates every 5-10s)
```

---

## 📞 Need Help?

### Common Questions:

**Q: How do I know if it's working?**
A: Look for the green blinking dot 🟢 next to "Live Dashboard" in sidebar

**Q: Can I run this 24/7?**  
A: Yes! The streaming script runs indefinitely until you stop it (Ctrl+C)

**Q: Will old data be deleted?**
A: No, all transactions are stored permanently in MySQL and HDFS

**Q: Can I change the products being sold?**
A: Yes! Edit the `PRODUCTS` list in `scripts/realtime_stream.py`

---

## 🎉 You're All Set!

Your real-time Big Data dashboard is now running! 

Enjoy watching your e-commerce analytics update live! 🚀

---

**Last Updated**: November 10, 2025
**Dashboard Version**: 2.0 (Real-time Edition)
