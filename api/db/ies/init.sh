
## Debugging: Print variables
echo -e "\nMSSQL_SA_PASSWORD: $MSSQL_SA_PASSWORD"
echo "MSSQL_DBUSER: $MSSQL_DBUSER"
echo "MSSQL_DBUSERPWD: $MSSQL_DBUSERPWD"
echo "MSSQL_DBNAME: $MSSQL_DBNAME"

echo "Current user: $(whoami)"
ls -ld /var/opt/mssql

## Wait for SQL Server to be ready
echo -e "\nWaiting for SQL Server to be ready..."
for i in {1..20}; do
    /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -Q "SELECT 1" &>/dev/null && break
    echo "SQL Server not ready yet. Retrying in 10 seconds..."
    sleep 10
done

## Check if database exists
echo -e "\nChecking if the database $MSSQL_DBNAME exists..."
SQL_QUERY="IF DB_ID(N''$MSSQL_DBNAME'') IS NOT NULL PRINT 'EXISTS'"
SQLCMD_OUTPUT=$(/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -Q "$SQL_QUERY" -W)
DB_EXISTS=$(echo $SQLCMD_OUTPUT | grep -o "EXISTS")

if [[ $DB_EXISTS == "EXISTS" ]]; then
    echo -e "\nThe database '$MSSQL_DBNAME' already exists."
else
    echo -e "\nCreating the dropout database/schema..."
    envsubst < tmp/sql/init.sql > tmp/sql/init.sql
    $sqlcmd_sa /tmp/sql/init.sql

    echo -e "\nExecuting table creation scripts..."
    envsubst < tmp/sql/creates.sql > tmp/sql/creates.sql
    $sqlcmd_sa /tmp/sql/creates.sql

    echo -e "\nExecuting dependency inserts..."
    envsubst < tmp/sql/inserts/dependencies.sql > tmp/sql/inserts/dependencies.sql
    $sqlcmd_user /tmp/sql/inserts/dependencies.sql

    echo -e "\nExecuting dropout inserts..."
    envsubst < tmp/sql/inserts/desertion.sql > tmp/sql/inserts/desertion.sql
    $sqlcmd_user /tmp/sql/inserts/desertion.sql

    echo -e "\nFinished setting up the dropout database."
fi
