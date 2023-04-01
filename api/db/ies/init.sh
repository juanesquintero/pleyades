/bin/bash -c "
    /opt/mssql/bin/sqlservr &
    /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P $MSSQL_SA_PASSWORD -i /tmp/init.sql &
    /opt/mssql-tools/bin/sqlcmd -S localhost -U $MSSQL_DBUSER -P $MSSQL_DBUSERPWD -i /tmp/creates.sql &
    /opt/mssql-tools/bin/sqlcmd -S localhost -U $MSSQL_DBUSER -P $MSSQL_DBUSERPWD -i /tmp/inserts/dependencias.sql &
    /opt/mssql-tools/bin/sqlcmd -S localhost -U $MSSQL_DBUSER -P $MSSQL_DBUSERPWD -i /tmp/inserts/desercion.sql
"