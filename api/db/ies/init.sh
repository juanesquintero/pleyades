## Open permissions to this file
chmod +x /tmp/init.sh

## Run MSSQLServer service
/opt/mssql/bin/sqlservr

## Reuse variables
sqlcmd='/opt/mssql-tools/bin/sqlcmd -S localhost -U'

sqlcmd_sa=$sqlcmd" sa -P $MSSQL_SA_PASSWORD -i"
sqlcmd_user=$sqlcmd" $MSSQL_DBUSER -P $MSSQL_DBUSERPWD -i"

YELLOW=$(tput setaf 3)
NC=$(tput setaf 7)

## Execute initial sql files

echo "${YELLOW}Inicializando la base de datos de deserción de SQL Server...${NC}"
$sqlcmd_sa /tmp/sql/init.sql

echo "${YELLOW}Ejecutando creates.sql...${NC}"
$sqlcmd_sa /tmp/sql/creates.sql

echo "${YELLOW}Ejecutando inserts dependencias.sql...${NC}"
$sqlcmd_user /tmp/sql/inserts/dependencias.sql

echo "${YELLOW}Ejecutando inserts desercion.sql...${NC}"
$sqlcmd_user /tmp/sql/inserts/desercion.sql

echo "${YELLOW}Finalizó la definicion de la bd de deserción!!!${NC}"
