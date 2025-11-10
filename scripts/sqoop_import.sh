#!/bin/bash
# Sqoop Import Helper - Phase 5.1
# Executes Sqoop imports with proper parameters

# MySQL Connection Info
MYSQL_HOST="mysql"
MYSQL_PORT="3306"
MYSQL_DB="testdb"
MYSQL_USER="sqoop"
MYSQL_PASSWORD="sqoop123"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║          Sqoop Import Operations                           ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Function: Import full table
import_full_table() {
    TABLE_NAME=$1
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Importing table: $TABLE_NAME"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    docker exec sqoop sqoop import \
        --connect jdbc:mysql://${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB} \
        --username ${MYSQL_USER} \
        --password ${MYSQL_PASSWORD} \
        --table ${TABLE_NAME} \
        --target-dir /user/sqoop/${TABLE_NAME} \
        --delete-target-dir \
        --m 1
    
    if [ $? -eq 0 ]; then
        echo "✅ Import completed for $TABLE_NAME"
    else
        echo "❌ Import failed for $TABLE_NAME"
    fi
    echo ""
}

# Function: Import with WHERE clause
import_with_filter() {
    TABLE_NAME=$1
    WHERE_CLAUSE=$2
    OUTPUT_DIR=$3
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Importing filtered data from: $TABLE_NAME"
    echo "   Filter: $WHERE_CLAUSE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    docker exec sqoop sqoop import \
        --connect jdbc:mysql://${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB} \
        --username ${MYSQL_USER} \
        --password ${MYSQL_PASSWORD} \
        --table ${TABLE_NAME} \
        --where "${WHERE_CLAUSE}" \
        --target-dir /user/sqoop/${OUTPUT_DIR} \
        --delete-target-dir \
        --m 1
    
    if [ $? -eq 0 ]; then
        echo "✅ Filtered import completed"
    else
        echo "❌ Filtered import failed"
    fi
    echo ""
}

# Function: Import with query
import_with_query() {
    QUERY=$1
    OUTPUT_DIR=$2
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Importing with custom query"
    echo "   Query: $QUERY"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    docker exec sqoop sqoop import \
        --connect jdbc:mysql://${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DB} \
        --username ${MYSQL_USER} \
        --password ${MYSQL_PASSWORD} \
        --query "${QUERY} WHERE \$CONDITIONS" \
        --target-dir /user/sqoop/${OUTPUT_DIR} \
        --delete-target-dir \
        --split-by transaction_id \
        --m 1
    
    if [ $? -eq 0 ]; then
        echo "✅ Query import completed"
    else
        echo "❌ Query import failed"
    fi
    echo ""
}

# Main execution
echo "════════════════════════════════════════════════════════════"
echo "Starting Sqoop Imports"
echo "════════════════════════════════════════════════════════════"
echo ""

# Wait for Sqoop container to be ready
echo "⏳ Waiting for Sqoop container..."
sleep 5

# Import all transactions
import_full_table "transactions"

# Import high-value transactions (>$100)
import_with_filter "transactions" "total_revenue > 100" "high_value_transactions"

# Import by region
import_with_filter "transactions" "region = 'North America'" "transactions_north_america"
import_with_filter "transactions" "region = 'Europe'" "transactions_europe"
import_with_filter "transactions" "region = 'Asia'" "transactions_asia"

# Import by category - Electronics
import_with_filter "transactions" "product_category = 'Electronics'" "transactions_electronics"

# Import with aggregation query
import_with_query "SELECT product_category, region, SUM(total_revenue) as total_revenue, COUNT(*) as transaction_count FROM transactions GROUP BY product_category, region" "category_region_summary"

echo "════════════════════════════════════════════════════════════"
echo "All Sqoop imports completed"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Verify HDFS: docker exec namenode hdfs dfs -ls -R /user/sqoop/"
echo "  2. Check data: docker exec namenode hdfs dfs -cat /user/sqoop/transactions/part-m-00000 | head -10"
echo ""
