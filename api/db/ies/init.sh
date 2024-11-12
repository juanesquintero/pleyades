## Set file permissions
chmod +x /tmp/init.sh

## Define variables
sqlcmd='/opt/mssql-tools/bin/sqlcmd -S localhost -U'

sqlcmd_sa=$sqlcmd" sa -P $MSSQL_SA_PASSWORD -i"
sqlcmd_user=$sqlcmd" $MSSQL_DBUSER -P $MSSQL_DBUSERPWD -i"


## Debugging: print variables
echo -e "\nMSSQL_SA_PASSWORD: $MSSQL_SA_PASSWORD"
echo "MSSQL_DBUSER: $MSSQL_DBUSER"
echo "MSSQL_DBUSERPWD: $MSSQL_DBUSERPWD"


## Wait for SQL Server to be ready
echo -e "\nWaiting for SQL Server to be up..."
sleep 75s

## Check if database already exists
echo -e "\nChecking if the database $MSSQL_DBNAME exists..."

SQL_QUERY="IF DB_ID(N'$MSSQL_DBNAME') IS NOT NULL PRINT 'EXISTS'"
SQLCMD_OUTPUT=$(/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -Q "$SQL_QUERY" -W)
DB_EXISTS=$(echo $SQLCMD_OUTPUT | grep -o "EXISTS")


if [[ $DB_EXISTS == "EXISTS" ]]; then
    echo -e "\nThe database '$MSSQL_DBNAME' already exists."
else
    ## Execute initial sql files
    echo -e "\nCreating the dropout database/schema..."
    $sqlcmd_sa /tmp/sql/init.sql

    echo "Executing table creation scripts..."
    $sqlcmd_sa /tmp/sql/creates.sql

    echo "Executing dependency inserts..."
    $sqlcmd_user /tmp/sql/inserts/dependencies.sql

    echo "Executing dropout inserts..."
    $sqlcmd_user /tmp/sql/inserts/desertion.sql

    echo -e "\nFinished setting up the dropout database."
fi
