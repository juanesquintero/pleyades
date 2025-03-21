## Reuse variables
sqlcmd='/opt/mssql-tools/bin/sqlcmd -S localhost -U'

sqlcmd_sa=$sqlcmd" sa -P $MSSQL_SA_PASSWORD"
sqlcmd_user=$sqlcmd" $MSSQL_DBUSER -P $MSSQL_DBUSERPWD"

## Debugging: Print variables
echo -e "\n\nMSSQL_SA_PASSWORD: $MSSQL_SA_PASSWORD"
echo "MSSQL_DBUSER: $MSSQL_DBUSER"
echo "MSSQL_DBUSERPWD: $MSSQL_DBUSERPWD"
echo -e "MSSQL_DBNAME: $MSSQL_DBNAME\n\n"

echo "Current user: $(whoami)"
ls -ld /var/opt/mssql

## Check if the environment variable is set to true
echo "DATA_INSERTED: $DATA_INSERTED"
if [[ "$DATA_INSERTED" == "true" ]]; then
    echo -e "\nData already inserted. Skipping creates and inserts."
    exit 0
fi

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

echo "DB_EXISTS: $DB_EXISTS"

if [[ $DB_EXISTS == "EXISTS" ]]; then
    echo -e "\nThe database '$MSSQL_DBNAME' already exists."
else
    echo -e "\nCreating the desertion database/schema..."
    $sqlcmd_sa -i /tmp/sql/init.sql

    echo -e "\nExecuting table creation scripts..."
    $sqlcmd_sa -i /tmp/sql/creates.sql

    echo -e "\nExecuting dependency inserts..."
    $sqlcmd_user -i /tmp/sql/inserts/dependencies.sql

    echo -e "\nExecuting desertion inserts..."
    $sqlcmd_user -i /tmp/sql/inserts/desertion.sql

    echo -e "\nFinished setting up the desertion database."

    # Set the environment variable to true after successful insertion
    export DATA_INSERTED="true"
    echo -e "\nDATA_INSERTED set to true."
fi
