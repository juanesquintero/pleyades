## Open permissions to this file
chmod +x /tmp/init.sh

YELLOW=$(tput setaf 3)
NC=$(tput setaf 7)

echo "${YELLOW}Inicializando la base de datos de deserción de SQL Server...${NC}"

## Run MSSQLServer service
/opt/mssql/bin/sqlservr

## Reuse variables
sqlcmd='/opt/mssql-tools/bin/sqlcmd -S localhost -U'

sqlcmd_sa=$sqlcmd" sa -P $MSSQL_SA_PASSWORD -i"
sqlcmd_user=$sqlcmd" $MSSQL_DBUSER -P $MSSQL_DBUSERPWD -i"


## Execute initial sql files

$sqlcmd_sa /tmp/sql/init.sql

$sqlcmd_sa /tmp/sql/creates.sql

$sqlcmd_user /tmp/sql/inserts/dependencias.sql

$sqlcmd_user /tmp/sql/inserts/desercion.sql

echo "${YELLOW}Finalizó la definicion de la bd de deserción!!!${NC}"
