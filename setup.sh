#!/bin/bash
# Setup Script - Prepares environment and makes everything executable
# Run this FIRST before anything else!

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Big Data Project - Initial Setup                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Get the script's directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Working directory: $SCRIPT_DIR"
echo ""

# Step 1: Check Docker
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[1/6] Checking Docker..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
    if docker ps &> /dev/null; then
        echo "✅ Docker is running"
    else
        echo "❌ Docker is not running. Please start Docker Desktop."
        exit 1
    fi
else
    echo "❌ Docker is not installed. Please install Docker Desktop."
    exit 1
fi
echo ""

# Step 2: Check Python
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[2/6] Checking Python..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python3 is installed: $PYTHON_VERSION"
else
    echo "❌ Python3 is not installed. Please install Python 3.7+."
    exit 1
fi
echo ""

# Step 3: Install Python packages
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[3/6] Installing Python packages..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
pip3 install --user pandas kafka-python mysql-connector-python pymysql sqlalchemy
if [ $? -eq 0 ]; then
    echo "✅ Python packages installed successfully"
else
    echo "⚠️  Some packages may have failed to install, but continuing..."
fi
echo ""

# Step 4: Make scripts executable
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[4/6] Making scripts executable..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
chmod +x scripts/*.sh
chmod +x *.sh 2>/dev/null
echo "✅ All shell scripts are now executable"
echo ""

# Step 5: Create necessary directories
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[5/6] Creating directories..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
mkdir -p logs/incoming
mkdir -p logs/.flume
mkdir -p sql
mkdir -p shared-data
echo "✅ All directories created"
echo ""

# Step 6: Start Docker containers
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[6/6] Starting Docker containers..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if docker-compose ps | grep -q "Up"; then
    echo "ℹ️  Some containers are already running"
    read -p "Restart all containers? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down
        docker-compose up -d
    fi
else
    docker-compose up -d
fi

echo ""
echo "⏳ Waiting for containers to be ready (30 seconds)..."
sleep 30
echo ""

# Verify containers
echo "📊 Container Status:"
docker-compose ps
echo ""

# Check if data file exists
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Checking data file..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "shared-data/Online Sales Data.csv" ]; then
    echo "✅ Data file found: shared-data/Online Sales Data.csv"
    FILE_SIZE=$(wc -l < "shared-data/Online Sales Data.csv")
    echo "   Total rows: $FILE_SIZE"
else
    echo "❌ Data file not found: shared-data/Online Sales Data.csv"
    echo "   Please ensure the CSV file is in the shared-data directory"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║              SETUP COMPLETED SUCCESSFULLY! ✅               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Option 1: Run complete pipeline automatically"
echo "  bash scripts/run_pipeline.sh"
echo ""
echo "Option 2: Run interactive demo"
echo "  bash scripts/demo.sh"
echo ""
echo "Option 3: Follow step-by-step guide"
echo "  Read QUICKSTART.md for detailed instructions"
echo ""
echo "📚 Documentation:"
echo "  • QUICKSTART.md - Quick start guide"
echo "  • PROJECT_COMPLETE.md - Project summary"
echo "  • scripts/README.md - Scripts documentation"
echo ""
