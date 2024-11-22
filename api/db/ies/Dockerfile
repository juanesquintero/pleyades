FROM mcr.microsoft.com/mssql/server:2022-latest

USER root

# Install required dependencies
RUN apt-get update && \
    apt-get install -y curl apt-transport-https gnupg gettext && \
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-archive-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-archive-keyring.gpg] https://packages.microsoft.com/ubuntu/22.04/prod jammy main" > /etc/apt/sources.list.d/mssql-release.list && \
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
