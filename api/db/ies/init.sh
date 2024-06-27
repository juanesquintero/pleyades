## Open permissions to this file
chmod +x /tmp/init.sh

## Reuse variables
sqlcmd='/opt/mssql-tools/bin/sqlcmd -S localhost -U'

sqlcmd_sa=$sqlcmd" sa -P $MSSQL_SA_PASSWORD -i"
sqlcmd_user=$sqlcmd" $MSSQL_DBUSER -P $MSSQL_DBUSERPWD -i"


## Debugging: print variables
echo "MSSQL_SA_PASSWORD: $MSSQL_SA_PASSWORD"
echo "MSSQL_DBUSER: $MSSQL_DBUSER"
echo "MSSQL_DBUSERPWD: $MSSQL_DBUSERPWD"


## Wait for SQL Server to be ready
echo "Esperando a que SQL Server este listo..."
sleep 90s

## Check if database already exists
echo "Checking if database $MSSQL_DBNAME exists..."

SQL_QUERY="IF DB_ID(N'$MSSQL_DBNAME') IS NOT NULL PRINT 'EXISTS'"
echo "SQL Query: $SQL_QUERY"

SQLCMD_OUTPUT=$(/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -Q "$SQL_QUERY" -W)
echo "SQLCMD Output: $SQLCMD_OUTPUT"

DB_EXISTS=$(echo $SQLCMD_OUTPUT | grep -o "EXISTS")

echo "DB_EXISTS: $DB_EXISTS"

if [[ $DB_EXISTS == "EXISTS" ]]; then
    echo "The database '$MSSQL_DBNAME' already exists."
else
    ## Execute initial sql files
    echo "Inicializando la base de datos de deserción..."
    $sqlcmd_sa /tmp/sql/init.sql

    echo "Ejecutando creates.sql..."
    $sqlcmd_sa /tmp/sql/creates.sql

    echo "Ejecutando inserts dependencias.sql..."
    $sqlcmd_user /tmp/sql/inserts/dependencias.sql

    echo "Ejecutando inserts desercion.sql..."
    $sqlcmd_user /tmp/sql/inserts/desercion.sql

    echo "Finalizó la definicion de la bd de deserción!!!"
fi