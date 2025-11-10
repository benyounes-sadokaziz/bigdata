# 📊 Big Data Dashboard - User Guide

## 🚀 Quick Start

### Start the Dashboard
```powershell
.\start-dashboard.ps1
```

The dashboard will automatically open in your browser at: **http://localhost:8501**

## 📋 Dashboard Features

### 1️⃣ **Overview Page**
- **System Status**: Real-time status of all Docker containers (MySQL, Kafka, HDFS, Sqoop)
- **Key Metrics**: 
  - Total transactions
  - Total revenue
  - Average transaction value
  - Number of products sold
- **Quick Charts**:
  - Revenue by product category
  - Sales distribution by region

### 2️⃣ **Sales Analytics**
- **Time Series Analysis**: Revenue trends over time
- **Top Products**: Top 10 products by revenue
- **Payment Analysis**: Revenue breakdown by payment method
- **Regional Performance**: Detailed metrics by region
- **Date Filters**: Filter data by custom date ranges

### 3️⃣ **Pipeline Status**
- **Container Health**: Status of all Docker containers
- **HDFS Browser**: View files in HDFS
- **Kafka Topics**: List of active Kafka topics
- **Data Flow Diagram**: Visual representation of data pipeline
- **Quick Actions**: Links to HDFS Web UI and pipeline controls

### 4️⃣ **Data Explorer**
- **Advanced Filters**: Filter by category, region, payment method
- **Data Table**: Interactive table with all transactions
- **Download**: Export filtered data to CSV
- **Statistics**: Real-time statistics for filtered data

## 🎨 Dashboard Controls

### Sidebar Features
- **Auto-refresh**: Enable automatic 30-second refresh
- **Manual Refresh**: Click to refresh data immediately
- **Navigation**: Switch between different dashboard pages

## 📊 Available Visualizations

1. **Bar Charts**: Category revenue, top products, payment methods
2. **Pie Charts**: Regional sales distribution
3. **Line Charts**: Revenue trends over time
4. **Data Tables**: Interactive sortable tables
5. **Metrics Cards**: Key performance indicators

## 🔧 Troubleshooting

### Dashboard Won't Start
```powershell
# Check if port 8501 is available
Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue

# If occupied, kill the process and restart
```

### No Data Showing
1. Check MySQL is running: `docker ps | findstr mysql`
2. Verify data exists: `docker exec mysql mysql -usqoop -psqoop123 testdb -e "SELECT COUNT(*) FROM transactions"`
3. Click "Refresh Now" in the sidebar

### Containers Showing Offline
```powershell
# Restart all containers
docker-compose restart

# Or restart specific container
docker restart mysql
```

## 💡 Tips & Tricks

1. **Auto-refresh**: Enable for live monitoring during data ingestion
2. **Filters**: Use multiple filters together in Data Explorer
3. **Download**: Export filtered data for external analysis
4. **Browser**: Use Chrome or Firefox for best performance
5. **Zoom**: Use Ctrl+Scroll to zoom charts

## 📈 Use Cases

### Monitoring Real-time Data Ingestion
1. Enable auto-refresh
2. Navigate to Overview page
3. Watch metrics update as Kafka streams data

### Analyzing Sales Performance
1. Go to Sales Analytics
2. Set date range
3. Review top products and regional performance

### System Health Check
1. Visit Pipeline Status page
2. Verify all containers are green
3. Check HDFS file count

### Data Export
1. Open Data Explorer
2. Apply desired filters
3. Click "Download CSV"

## 🌐 URLs

- **Dashboard**: http://localhost:8501
- **HDFS Web UI**: http://localhost:9870
- **Hadoop File Browser**: http://localhost:9870/explorer.html#/user

## 🛑 Stopping the Dashboard

Press `Ctrl+C` in the PowerShell window running the dashboard.

---

## 📞 Need Help?

Run the test script to verify your pipeline:
```powershell
.\test-pipeline.ps1
```

Check container logs:
```powershell
docker logs mysql
docker logs kafka
docker logs namenode
```
