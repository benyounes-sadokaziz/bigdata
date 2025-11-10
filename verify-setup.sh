#!/bin/bash

echo "=========================================="
echo "Big Data Environment Setup Verification"
echo "=========================================="
echo ""

# Check if Docker is running
echo "1. Checking Docker..."
if docker ps > /dev/null 2>&1; then
    echo "✓ Docker is running"
else
    echo "✗ Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo ""
echo "2. Checking Docker Compose..."
if docker-compose --version > /dev/null 2>&1; then
    echo "✓ Docker Compose is available"
    docker-compose --version
else
    echo "✗ Docker Compose not found"
    exit 1
fi

echo ""
echo "3. Checking required files..."
files=("docker-compose.yml" "hadoop.env" "sqoop/Dockerfile" "flume/Dockerfile")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file not found"
        exit 1
    fi
done

echo ""
echo "=========================================="
echo "Setup looks good! Ready to proceed."
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run: docker-compose up -d"
echo "2. Wait 60 seconds for services to initialize"
echo "3. Check status: docker-compose ps"
echo "4. Follow the testing instructions in README.md"
echo ""
