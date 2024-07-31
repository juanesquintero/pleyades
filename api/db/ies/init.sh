## Open permissions to this file
chmod +x /tmp/init.sh

## Reuse variables
sqlcmd='/opt/mssql-tools/bin/sqlcmd -S localhost -U'

sqlcmd_sa=$sqlcmd" sa -P $MSSQL_SA_PASSWORD -i"
sqlcmd_user=$sqlcmd" $MSSQL_DBUSER -P $MSSQL_DBUSERPWD -i"


## Debugging: print variables
echo -e "\nMSSQL_SA_PASSWORD: $MSSQL_SA_PASSWORD"
echo "MSSQL_DBUSER: $MSSQL_DBUSER"
echo "MSSQL_DBUSERPWD: $MSSQL_DBUSERPWD"


## Wait for SQL Server to be ready
echo -e "\nEsperando a que el servicio de SQL Server este arriba..."
sleep 75s

## Check if database already exists
echo -e "\nComprobando si la base de datos $MSSQL_DBNAME existe..."

SQL_QUERY="IF DB_ID(N'$MSSQL_DBNAME') IS NOT NULL PRINT 'EXISTS'"
SQLCMD_OUTPUT=$(/opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -Q "$SQL_QUERY" -W)
DB_EXISTS=$(echo $SQLCMD_OUTPUT | grep -o "EXISTS")


if [[ $DB_EXISTS == "EXISTS" ]]; then
    echo -e "\nLa base de datos '$MSSQL_DBNAME' ya existe."
else
    ## Execute initial sql files
    echo -e "\nCreando la bd/schema de deserción..."
    $sqlcmd_sa /tmp/sql/init.sql

    echo "Ejecutando creates tables..."
    $sqlcmd_sa /tmp/sql/creates.sql

    echo "Ejecutando inserts dependencias.sql..."
    $sqlcmd_user /tmp/sql/inserts/dependencias.sql

    echo "Ejecutando inserts desercion.sql..."
    $sqlcmd_user /tmp/sql/inserts/desercion.sql

    echo -e "\nFinalizó la definicion de la bd de deserción."
fi
