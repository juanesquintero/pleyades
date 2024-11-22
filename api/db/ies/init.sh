## Reuse variables
sqlcmd='/opt/mssql-tools/bin/sqlcmd -S localhost -U'

sqlcmd_sa=$sqlcmd" sa -P $MSSQL_SA_PASSWORD"
sqlcmd_user=$sqlcmd" $MSSQL_DBUSER -P $MSSQL_DBUSERPWD"

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
    $sqlcmd_sa -Q "SELECT 1" &>/dev/null && break
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
    $sqlcmd_sa -i /tmp/sql/init.sql

    echo -e "\nExecuting table creation scripts..."
    $sqlcmd_sa -i /tmp/sql/creates.sql

    echo -e "\nExecuting dependency inserts..."
    $sqlcmd_user -i /tmp/sql/inserts/dependencies.sql

    echo -e "\nExecuting dropout inserts..."
    $sqlcmd_user -i /tmp/sql/inserts/desertion.sql

    echo -e "\nFinished setting up the dropout database."
fi

