FROM mcr.microsoft.com/mssql/server:2022-latest

USER root

# Install required dependencies
RUN apt-get update && \
    apt-get install -y curl apt-transport-https gnupg && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list -o /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y mssql-tools unixodbc-dev && \
    apt-get clean

# Add mssql-tools to the PATH for all users
ENV PATH="/opt/mssql-tools/bin:$PATH"

# Copy SQL scripts and initialization script
COPY ./sql /tmp/sql
COPY ./init.sh /tmp/init.sh

# Ensure proper permissions for scripts
RUN chmod -R 755 /tmp/sql && chmod +x /tmp/init.sh && chown -R mssql:root /tmp/sql

USER mssql

# Default command to run SQL Server and initialization script
CMD ["/bin/bash", "-c", "/opt/mssql/bin/sqlservr & /tmp/init.sh && wait"]
