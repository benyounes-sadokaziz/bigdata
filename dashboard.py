"""
Big Data Pipeline Dashboard - Streamlit
Real-time visualization of E-commerce Sales Data Pipeline
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import subprocess
import json
from datetime import datetime
import time
from sqlalchemy import create_engine
from kafka import KafkaConsumer
import os
import warnings

# Suppress specific warnings
warnings.filterwarnings('ignore', category=UserWarning)

# Page configuration
st.set_page_config(
    page_title="Big Data Pipeline Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for real-time updates
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 5

# Custom CSS
st.markdown("""
    <style>
    /* Main color scheme */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #7c3aed;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --dark-bg: #1e293b;
        --card-bg: #ffffff;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    
    /* Header styling */
    h1 {
        color: #1e293b;
        font-weight: 700;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    h2 {
        color: #334155;
        font-weight: 600;
        font-size: 1.75rem !important;
        margin-top: 1.5rem !important;
    }
    
    h3 {
        color: #475569;
        font-weight: 600;
        font-size: 1.25rem !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.875rem;
    }
    
    /* Card styling */
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Status indicators */
    .status-online {
        color: #10b981;
        font-weight: 600;
    }
    
    .status-offline {
        color: #ef4444;
        font-weight: 600;
    }
    
    /* Live indicator */
    .live-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        }
        50% {
            box-shadow: 0 0 0 10px rgba(16, 185, 129, 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
        }
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #e2e8f0;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #f1f5f9 !important;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
        box-shadow: 0 6px 8px -1px rgba(37, 99, 235, 0.4);
        transform: translateY(-2px);
    }
    
    /* Radio button styling */
    [data-testid="stSidebar"] .stRadio > label {
        color: #f1f5f9 !important;
        font-weight: 500;
    }
    
    /* Checkbox styling */
    [data-testid="stSidebar"] .stCheckbox > label {
        color: #f1f5f9 !important;
        font-weight: 500;
    }
    
    /* Slider styling */
    [data-testid="stSidebar"] .stSlider > label {
        color: #f1f5f9 !important;
    }
    
    /* Transaction feed styling */
    .transaction-row {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid #2563eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }
    
    .transaction-row:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transform: translateX(4px);
    }
    
    /* Chart container */
    .plot-container {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Caption styling */
    .caption {
        color: #64748b;
        font-size: 0.875rem;
        font-style: italic;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e2e8f0;
    }
    
    /* Success message */
    .success-box {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Warning box */
    .warning-box {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Helper Functions
@st.cache_data(ttl=5)  # Reduced TTL to 5 seconds for real-time updates
def get_mysql_data():
    """Fetch data from MySQL"""
    try:
        # Use SQLAlchemy engine for pandas compatibility
        engine = create_engine('mysql+mysqlconnector://root:rootpassword@localhost:3306/testdb')
        query = "SELECT * FROM transactions"
        df = pd.read_sql(query, engine)
        engine.dispose()
        
        # Convert data types for proper handling
        if not df.empty:
            df['transaction_id'] = pd.to_numeric(df['transaction_id'], errors='coerce')
            if 'units_sold' in df.columns:
                df['quantity'] = df['units_sold']
            if 'total_revenue' in df.columns:
                df['total_amount'] = df['total_revenue']
            if 'date' in df.columns:
                df['timestamp'] = pd.to_datetime(df['date'], errors='coerce')
            
            df['quantity'] = pd.to_numeric(df.get('quantity', df.get('units_sold', 0)), errors='coerce')
            df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
            df['total_amount'] = pd.to_numeric(df.get('total_amount', df.get('total_revenue', 0)), errors='coerce')
            
            # Add aliases for compatibility
            if 'product_category' not in df.columns and 'category' in df.columns:
                df['product_category'] = df['category']
            if 'total_revenue' not in df.columns and 'total_amount' in df.columns:
                df['total_revenue'] = df['total_amount']
            if 'timestamp' in df.columns:
                df['date'] = pd.to_datetime(df['timestamp']).dt.date
        
        return df
    except Exception as e:
        st.error(f"MySQL Error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=30)
def get_hdfs_files():
    """Get list of files in HDFS"""
    try:
        result = subprocess.run(
            ['docker', 'exec', 'namenode', 'hdfs', 'dfs', '-ls', '-R', '/user'],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

@st.cache_data(ttl=30)
def get_kafka_topics():
    """Get Kafka topics"""
    try:
        result = subprocess.run(
            ['docker', 'exec', 'kafka', 'kafka-topics', '--bootstrap-server', 
             'localhost:9092', '--list'],
            capture_output=True,
            text=True
        )
        return [t.strip() for t in result.stdout.split('\n') if t.strip()]
    except Exception as e:
        return []

def check_container_status(container_name):
    """Check if a Docker container is running"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', f'name={container_name}', '--format', '{{.Status}}'],
            capture_output=True,
            text=True
        )
        return 'Up' in result.stdout
    except:
        return False

# Main Dashboard
def main():
    # Modern Header with gradient
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 10px 25px rgba(102, 126, 234, 0.2);'>
            <h1 style='color: white; margin: 0; font-size: 2.5rem; font-weight: 800;'>
                📊 Big Data Pipeline Dashboard
            </h1>
            <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
                Real-time E-Commerce Sales Analytics Platform
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        # Logo/Header
        st.markdown("""
            <div style='text-align: center; padding: 1.5rem 0; background: rgba(255,255,255,0.1); 
                        border-radius: 10px; margin-bottom: 1rem;'>
                <h2 style='color: #f1f5f9; margin: 0; font-size: 1.5rem;'>⚡ Control Panel</h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Real-time controls with better styling
        st.markdown("""
            <div style='background: rgba(16, 185, 129, 0.1); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
                <div style='display: flex; align-items: center; margin-bottom: 0.5rem;'>
                    <span class="live-indicator"></span>
                    <span style='color: #10b981; font-weight: 600; font-size: 1.1rem;'>Live Dashboard</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.session_state.auto_refresh = st.checkbox("🔄 Auto-refresh", value=st.session_state.auto_refresh)
        
        if st.session_state.auto_refresh:
            st.session_state.refresh_interval = st.slider(
                "⏱️ Refresh interval (seconds)", 
                min_value=2, 
                max_value=30, 
                value=st.session_state.refresh_interval
            )
            st.caption(f"⏳ Next refresh in {st.session_state.refresh_interval}s")
            
        if st.button("🔄 Refresh Now", width='stretch'):
            st.cache_data.clear()
            st.session_state.last_update = datetime.now()
            st.rerun()
        
        st.markdown("---")
        
        # Last update with icon
        st.markdown(f"""
            <div style='background: rgba(255,255,255,0.1); padding: 0.75rem; border-radius: 6px; text-align: center;'>
                <span style='color: #94a3b8; font-size: 0.85rem;'>🕐 Last update</span><br/>
                <span style='color: #f1f5f9; font-weight: 600;'>{st.session_state.last_update.strftime('%H:%M:%S')}</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation with icons
        st.markdown("### 📋 Navigation")
        page = st.radio(
            "Select View:", 
            ["📈 Overview", "💰 Sales Analytics", "🔧 Pipeline Status", "🔍 Data Explorer"],
            label_visibility="collapsed"
        )
    
    # Auto-refresh logic (after sidebar to avoid issues)
    if st.session_state.auto_refresh:
        time.sleep(st.session_state.refresh_interval)
        st.cache_data.clear()
        st.session_state.last_update = datetime.now()
        st.rerun()
    
    # Page routing
    if page == "📈 Overview":
        show_overview()
    elif page == "💰 Sales Analytics":
        show_sales_analytics()
    elif page == "🔧 Pipeline Status":
        show_pipeline_status()
    elif page == "🔍 Data Explorer":
        show_data_explorer()

def show_overview():
    """Overview dashboard with modern design"""
    
    # Section Header
    st.markdown("""
        <h2 style='color: #1e293b; margin-bottom: 1.5rem; display: flex; align-items: center;'>
            <span style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         padding: 0.5rem; border-radius: 8px; margin-right: 1rem;'>📈</span>
            System Overview
        </h2>
    """, unsafe_allow_html=True)
    
    # System Status Cards with modern design
    col1, col2, col3, col4 = st.columns(4)
    
    containers = {
        "MySQL": check_container_status("mysql"),
        "Kafka": check_container_status("kafka"),
        "HDFS": check_container_status("namenode"),
        "Sqoop": check_container_status("sqoop")
    }
    
    with col1:
        status_icon = "🟢" if containers["MySQL"] else "🔴"
        status_text = "Online" if containers["MySQL"] else "Offline"
        st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid {"#10b981" if containers["MySQL"] else "#ef4444"};'>
                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{status_icon}</div>
                <div style='color: #64748b; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;'>MySQL</div>
                <div style='color: #1e293b; font-size: 1.25rem; font-weight: 700; margin-top: 0.25rem;'>{status_text}</div>
                <div style='color: #94a3b8; font-size: 0.75rem; margin-top: 0.25rem;'>↑ Database</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        status_icon = "🟢" if containers["Kafka"] else "🔴"
        status_text = "Online" if containers["Kafka"] else "Offline"
        st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid {"#10b981" if containers["Kafka"] else "#ef4444"};'>
                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{status_icon}</div>
                <div style='color: #64748b; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;'>Kafka</div>
                <div style='color: #1e293b; font-size: 1.25rem; font-weight: 700; margin-top: 0.25rem;'>{status_text}</div>
                <div style='color: #94a3b8; font-size: 0.75rem; margin-top: 0.25rem;'>↑ Streaming</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        status_icon = "🟢" if containers["HDFS"] else "🔴"
        status_text = "Online" if containers["HDFS"] else "Offline"
        st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid {"#10b981" if containers["HDFS"] else "#ef4444"};'>
                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{status_icon}</div>
                <div style='color: #64748b; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;'>HDFS</div>
                <div style='color: #1e293b; font-size: 1.25rem; font-weight: 700; margin-top: 0.25rem;'>{status_text}</div>
                <div style='color: #94a3b8; font-size: 0.75rem; margin-top: 0.25rem;'>↑ Storage</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        status_icon = "🟢" if containers["Sqoop"] else "🔴"
        status_text = "Online" if containers["Sqoop"] else "Offline"
        st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 4px solid {"#10b981" if containers["Sqoop"] else "#ef4444"};'>
                <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{status_icon}</div>
                <div style='color: #64748b; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em;'>Sqoop</div>
                <div style='color: #1e293b; font-size: 1.25rem; font-weight: 700; margin-top: 0.25rem;'>{status_text}</div>
                <div style='color: #94a3b8; font-size: 0.75rem; margin-top: 0.25rem;'>↑ ETL Tool</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Data Metrics
    df = get_mysql_data()
    
    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Transactions",
                f"{len(df):,}",
                delta=None
            )
        
        with col2:
            total_revenue = df['total_revenue'].sum()
            st.metric(
                "Total Revenue",
                f"${total_revenue:,.2f}",
                delta=None
            )
        
        with col3:
            avg_transaction = df['total_revenue'].mean()
            st.metric(
                "Avg Transaction",
                f"${avg_transaction:.2f}",
                delta=None
            )
        
        with col4:
            unique_products = df['product_name'].nunique()
            st.metric(
                "Products Sold",
                f"{unique_products}",
                delta=None
            )
        
        st.markdown("---")
        
        # Quick Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Revenue by Category")
            category_revenue = df.groupby('product_category')['total_revenue'].sum().reset_index()
            category_revenue = category_revenue.sort_values('total_revenue', ascending=False)
            
            fig = px.bar(
                category_revenue,
                x='product_category',
                y='total_revenue',
                color='total_revenue',
                color_continuous_scale='Blues',
                labels={'total_revenue': 'Revenue ($)', 'product_category': 'Category'}
            )
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            st.subheader("🌍 Sales by Region")
            region_sales = df.groupby('region')['total_revenue'].sum().reset_index()
            
            fig = px.pie(
                region_sales,
                values='total_revenue',
                names='region',
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, width='stretch')
        
        # Real-time Transaction Feed
        st.markdown("---")
        st.subheader("🔴 Live Transaction Feed")
        st.caption("Latest 10 transactions (Auto-refreshes when enabled)")
        
        # Get latest transactions
        try:
            # Sort by transaction_id and get top 10
            latest_df = df.nlargest(10, 'transaction_id')
            
            # Display as styled dataframe
            for idx, row in latest_df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 2])
                with col1:
                    st.markdown(f"**#{int(row['transaction_id'])}**")
                with col2:
                    st.markdown(f"{row['product_name']}")
                with col3:
                    st.markdown(f"{int(row['quantity'])}x")
                with col4:
                    st.markdown(f"**${row['total_revenue']:.2f}**")
                with col5:
                    timestamp_str = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['timestamp']) else 'N/A'
                    st.caption(f"{row['region']} • {timestamp_str}")
                st.markdown("---")
        except Exception as e:
            st.warning(f"Could not load transaction feed: {e}")
            st.info("Transactions will appear here as they are generated...")

def show_sales_analytics():
    """Sales Analytics Dashboard"""
    st.header("💰 Sales Analytics")
    
    df = get_mysql_data()
    
    if df.empty:
        st.warning("No data available in MySQL")
        return
    
    # Convert date column
    df['date'] = pd.to_datetime(df['date'])
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", df['date'].min())
    with col2:
        end_date = st.date_input("End Date", df['date'].max())
    
    # Filter data
    mask = (df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))
    filtered_df = df[mask]
    
    st.markdown("---")
    
    # Time Series Analysis with Real-time indicator
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader("📈 Revenue Trend Over Time")
    with col2:
        if st.session_state.auto_refresh:
            st.markdown('<div style="text-align: right;"><span class="live-indicator"></span> <span>Live Updates</span></div>', unsafe_allow_html=True)
    
    daily_revenue = filtered_df.groupby('date')['total_revenue'].sum().reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_revenue['date'],
        y=daily_revenue['total_revenue'],
        mode='lines+markers',
        name='Daily Revenue',
        line=dict(color='#0066cc', width=2),
        marker=dict(size=6)
    ))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig, width='stretch')
    
    # Product Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 Products by Revenue")
        top_products = filtered_df.groupby('product_name')['total_revenue'].sum().reset_index()
        top_products = top_products.sort_values('total_revenue', ascending=False).head(10)
        
        fig = px.bar(
            top_products,
            x='total_revenue',
            y='product_name',
            orientation='h',
            color='total_revenue',
            color_continuous_scale='Viridis',
            labels={'total_revenue': 'Revenue ($)', 'product_name': 'Product'}
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("💳 Payment Method Distribution")
        payment_dist = filtered_df.groupby('payment_method')['total_revenue'].sum().reset_index()
        
        fig = px.bar(
            payment_dist,
            x='payment_method',
            y='total_revenue',
            color='payment_method',
            labels={'total_revenue': 'Revenue ($)', 'payment_method': 'Payment Method'}
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, width='stretch')
    
    # Regional Analysis
    st.subheader("🗺️ Regional Performance")
    region_metrics = filtered_df.groupby('region').agg({
        'total_revenue': 'sum',
        'transaction_id': 'count',
        'quantity': 'sum'
    }).reset_index()
    region_metrics.columns = ['Region', 'Total Revenue', 'Transactions', 'Units Sold']
    region_metrics['Avg Transaction'] = region_metrics['Total Revenue'] / region_metrics['Transactions']
    
    st.dataframe(
        region_metrics.style.format({
            'Total Revenue': '${:,.2f}',
            'Avg Transaction': '${:,.2f}'
        }),
        width='stretch'
    )

def show_pipeline_status():
    """Pipeline Status Dashboard"""
    st.header("🔧 Pipeline Status")
    
    # Container Status
    st.subheader("🐳 Docker Containers")
    containers = ["mysql", "kafka", "zookeeper", "namenode", "datanode", "sqoop", "flume"]
    
    status_data = []
    for container in containers:
        is_running = check_container_status(container)
        status_data.append({
            'Container': container.capitalize(),
            'Status': '🟢 Running' if is_running else '🔴 Stopped',
            'Health': 'Healthy' if is_running else 'Down'
        })
    
    status_df = pd.DataFrame(status_data)
    st.dataframe(status_df, width='stretch', hide_index=True)
    
    st.markdown("---")
    
    # HDFS Status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💾 HDFS File System")
        hdfs_output = get_hdfs_files()
        st.code(hdfs_output, language='bash')
    
    with col2:
        st.subheader("📡 Kafka Topics")
        topics = get_kafka_topics()
        if topics:
            for topic in topics:
                st.write(f"✓ {topic}")
        else:
            st.warning("No Kafka topics found")
    
    st.markdown("---")
    
    # Data Flow Diagram
    st.subheader("📊 Data Flow")
    st.markdown("""
    ```
    ┌─────────────┐
    │ MySQL (100) │ ──────┐
    └─────────────┘       │
                          ▼
                    ┌──────────┐
                    │   HDFS   │
                    └──────────┘
                          ▲
    ┌─────────────┐       │
    │ Kafka (72)  │ ──────┘
    └─────────────┘       
                          ▲
    ┌─────────────┐       │
    │  Logs (5K)  │ ──────┘
    └─────────────┘
    ```
    """)
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Open HDFS UI"):
            st.markdown("[HDFS Web UI](http://localhost:9870)", unsafe_allow_html=True)
    
    with col2:
        if st.button("🔄 Restart Pipeline"):
            st.info("Run: `docker-compose restart`")
    
    with col3:
        if st.button("📈 Run Tests"):
            st.info("Run: `.\test-pipeline.ps1`")

def show_data_explorer():
    """Data Explorer"""
    st.header("🔍 Data Explorer")
    
    df = get_mysql_data()
    
    if df.empty:
        st.warning("No data available")
        return
    
    # Filters
    st.subheader("🎯 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        categories = ['All'] + list(df['product_category'].unique())
        selected_category = st.selectbox("Category", categories)
    
    with col2:
        regions = ['All'] + list(df['region'].unique())
        selected_region = st.selectbox("Region", regions)
    
    with col3:
        payments = ['All'] + list(df['payment_method'].unique())
        selected_payment = st.selectbox("Payment Method", payments)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['product_category'] == selected_category]
    if selected_region != 'All':
        filtered_df = filtered_df[filtered_df['region'] == selected_region]
    if selected_payment != 'All':
        filtered_df = filtered_df[filtered_df['payment_method'] == selected_payment]
    
    # Display data
    st.subheader(f"📊 Data Table ({len(filtered_df)} records)")
    st.dataframe(
        filtered_df.style.format({
            'unit_price': '${:.2f}',
            'total_revenue': '${:.2f}'
        }),
        width='stretch',
        height=400
    )
    
    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"sales_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Statistics
    st.subheader("📈 Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Records", len(filtered_df))
    with col2:
        st.metric("Total Revenue", f"${filtered_df['total_revenue'].sum():,.2f}")
    with col3:
        st.metric("Avg Revenue", f"${filtered_df['total_revenue'].mean():.2f}")
    with col4:
        st.metric("Total Units", f"{filtered_df['quantity'].sum():,}")

if __name__ == "__main__":
    main()
