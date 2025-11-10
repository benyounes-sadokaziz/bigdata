#!/bin/bash

# Script to generate sample log files for Flume testing

LOG_DIR="/logs/incoming"
LOG_LEVELS=("INFO" "WARN" "ERROR" "DEBUG")
SERVICES=("WebServer" "Database" "API" "Cache" "Queue")

# Create log directory if it doesn't exist
mkdir -p $LOG_DIR

echo "Starting log generation..."

# Generate 5 log files
for i in {1..5}; do
    FILENAME="application_$(date +%Y%m%d_%H%M%S)_$i.log"
    FILEPATH="$LOG_DIR/$FILENAME"
    
    echo "Generating log file: $FILENAME"
    
    # Generate 50 log entries per file
    for j in {1..50}; do
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        LEVEL=${LOG_LEVELS[$RANDOM % ${#LOG_LEVELS[@]}]}
        SERVICE=${SERVICES[$RANDOM % ${#SERVICES[@]}]}
        REQUEST_ID=$(uuidgen 2>/dev/null || echo "REQ-$RANDOM")
        
        case $LEVEL in
            "INFO")
                MESSAGE="Request processed successfully"
                ;;
            "WARN")
                MESSAGE="High memory usage detected: ${RANDOM}%"
                ;;
            "ERROR")
                MESSAGE="Connection timeout to external service"
                ;;
            "DEBUG")
                MESSAGE="Function execution time: ${RANDOM}ms"
                ;;
        esac
        
        # Write log entry
        echo "$TIMESTAMP [$LEVEL] [$SERVICE] [RequestID: $REQUEST_ID] - $MESSAGE" >> $FILEPATH
    done
    
    echo "Generated $FILENAME with 50 entries"
    sleep 2
done

echo "Log generation completed!"
echo "Generated 5 log files in $LOG_DIR"
