#!/bin/bash
# Sqoop Export Helper - Phase 5.2
# Exports processed data from HDFS back to MySQL

# MySQL Connection Info
MYSQL_HOST="mysql"
MYSQL_PORT="3306"
MYSQL_DB="testdb"
MYSQL_USER="sqoop"
MYSQL_PASSWORD="sqoop123"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Sqoop Export Operations                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Function: Export from HDFS to MySQL
export_to_mysql() {
    SOURCE_DIR=$1
    TARGET_TABLE=$2
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📤 Exporting from HDFS to MySQL"
    echo "   Source: $SOURCE_DIR"
    echo "   Target Table: $TARGET_TABLE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    docker exec sqoop sqoop export \
        --connect jdbc:mysql://${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB} \
        --username ${MYSQL_USER} \
        --password ${MYSQL_PASSWORD} \
        --table ${TARGET_TABLE} \
        --export-dir ${SOURCE_DIR} \
        --input-fields-terminated-by ',' \
        --m 1
    
    if [ $? -eq 0 ]; then
        echo "✅ Export completed"
    else
        echo "❌ Export failed"
    fi
    echo ""
}

# Main execution
echo "════════════════════════════════════════════════════════════"
echo "Starting Sqoop Exports"
echo "════════════════════════════════════════════════════════════"
echo ""

# Example: Export aggregated results
# Note: You need to create the target table in MySQL first
# export_to_mysql "/user/sqoop/category_region_summary" "category_summary"

echo "⚠️  Export operations require target tables to exist in MySQL"
echo "   Create tables manually before running exports"
echo ""
echo "Example usage:"
echo "  export_to_mysql '/user/sqoop/results' 'target_table'"
echo ""
