#!/bin/bash
# Flume Starter Script - Phase 7.2
# Starts both Flume agents (logs and Kafka)

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Flume Agent Starter                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if Flume container is running
if ! docker ps | grep -q "flume"; then
    echo "❌ Error: Flume container is not running"
    echo "   Please run: docker-compose up -d flume"
    exit 1
fi

# Check if config files exist
if [ ! -f "flume-conf/flume-logs.conf" ] || [ ! -f "flume-conf/flume-kafka.conf" ]; then
    echo "❌ Error: Flume configuration files not found"
    exit 1
fi

echo "🚀 Starting Flume agents..."
echo ""

# Start log processing agent
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Starting log-agent (Log File Processor)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker exec -d flume bash -c "flume-ng agent \
    --conf /opt/flume/conf \
    --conf-file /opt/flume/conf/flume-logs.conf \
    --name log-agent \
    -Dflume.root.logger=INFO,console \
    > /opt/flume/logs/log-agent.log 2>&1"

if [ $? -eq 0 ]; then
    echo "✅ log-agent started successfully"
else
    echo "❌ Failed to start log-agent"
fi

sleep 3

# Start Kafka consumer agent
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Starting kafka-agent (Kafka Consumer)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

docker exec -d flume bash -c "flume-ng agent \
    --conf /opt/flume/conf \
    --conf-file /opt/flume/conf/flume-kafka.conf \
    --name kafka-agent \
    -Dflume.root.logger=INFO,console \
    > /opt/flume/logs/kafka-agent.log 2>&1"

if [ $? -eq 0 ]; then
    echo "✅ kafka-agent started successfully"
else
    echo "❌ Failed to start kafka-agent"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Flume Agents Started ✅                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Monitoring Commands:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Check log-agent logs:"
echo "  docker exec flume tail -f /opt/flume/logs/log-agent.log"
echo ""
echo "Check kafka-agent logs:"
echo "  docker exec flume tail -f /opt/flume/logs/kafka-agent.log"
echo ""
echo "List Flume processes:"
echo "  docker exec flume ps aux | grep flume"
echo ""
echo "Stop agents:"
echo "  docker exec flume pkill -f flume-ng"
echo ""
