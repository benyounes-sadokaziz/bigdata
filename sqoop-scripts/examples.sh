#!/bin/bash

# Sqoop example scripts for your Big Data project

echo "=== Sqoop Example Scripts ==="
echo ""

# 1. Import employees table from MySQL to HDFS
echo "1. Import employees table to HDFS:"
echo "sqoop import \\"
echo "  --connect jdbc:mysql://mysql:3306/testdb \\"
echo "  --username sqoop \\"
echo "  --password sqoop123 \\"
echo "  --table employees \\"
echo "  --target-dir /user/sqoop/employees \\"
echo "  --m 1"
echo ""

# 2. Import with where clause
echo "2. Import with WHERE clause (IT department only):"
echo "sqoop import \\"
echo "  --connect jdbc:mysql://mysql:3306/testdb \\"
echo "  --username sqoop \\"
echo "  --password sqoop123 \\"
echo "  --table employees \\"
echo "  --where \"department='IT'\" \\"
echo "  --target-dir /user/sqoop/employees_it \\"
echo "  --m 1"
echo ""

# 3. Import all tables
echo "3. Import all tables from database:"
echo "sqoop import-all-tables \\"
echo "  --connect jdbc:mysql://mysql:3306/testdb \\"
echo "  --username sqoop \\"
echo "  --password sqoop123 \\"
echo "  --warehouse-dir /user/sqoop/warehouse \\"
echo "  --m 1"
echo ""

# 4. Export data from HDFS to MySQL
echo "4. Export data from HDFS back to MySQL:"
echo "sqoop export \\"
echo "  --connect jdbc:mysql://mysql:3306/testdb \\"
echo "  --username sqoop \\"
echo "  --password sqoop123 \\"
echo "  --table employees \\"
echo "  --export-dir /user/sqoop/employees \\"
echo "  --m 1"
echo ""

# 5. Incremental import
echo "5. Incremental import (append mode):"
echo "sqoop import \\"
echo "  --connect jdbc:mysql://mysql:3306/testdb \\"
echo "  --username sqoop \\"
echo "  --password sqoop123 \\"
echo "  --table sales \\"
echo "  --target-dir /user/sqoop/sales \\"
echo "  --incremental append \\"
echo "  --check-column sale_id \\"
echo "  --last-value 0 \\"
echo "  --m 1"
echo ""

# 6. Import with custom query
echo "6. Import with custom SQL query:"
echo "sqoop import \\"
echo "  --connect jdbc:mysql://mysql:3306/testdb \\"
echo "  --username sqoop \\"
echo "  --password sqoop123 \\"
echo "  --query 'SELECT first_name, last_name, salary FROM employees WHERE salary > 70000 AND \$CONDITIONS' \\"
echo "  --target-dir /user/sqoop/high_salary_employees \\"
echo "  --split-by emp_id \\"
echo "  --m 1"
echo ""

echo "=== End of Sqoop Examples ==="
