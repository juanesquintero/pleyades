FROM python:3.8-slim

WORKDIR /app
RUN apt-get update && apt-get install -y gnupg curl openssl ca-certificates
RUN update-ca-certificates

#······················ MS SQL SERVER Driver ······················
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

#Download appropriate package for the OS version (Debian 11)
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17
# optional: for bcp and sqlcmd
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN . ~/.bashrc
# optional: for unixODBC development headers
RUN apt-get install -y unixodbc-dev
# optional: kerberos library for debian-slim distributions
RUN apt-get install -y libgssapi-krb5-2


#······················ Python App ······················
# Update pip
RUN pip install --upgrade pip

# Copy resources
COPY . /app

# Install requirements
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


#······················ OS config ······················
# Update TSL protocol to MySQL
RUN sed -i -E 's/MinProtocol[=\ ]+.*/MinProtocol = TLSv1.0/g' /etc/ssl/openssl.cnf

# Expose port
EXPOSE 80
