# PLEYADES 
(PLataforma de Exploración Y Analítica para la Desercion EStudiantil)

----------

<small>
</small>
<br>

# Setup
Clone the repository
```console
$ git clone https://gitlab.com/pleyades1/pleyades-educatic.git
```

Create the .env files from the .env.template 

###  /.env
```env
IES_CLIENT=ies_client_short_name
DB_ROOT_PWD=pleyades_db_root_password
PUBLIC_PORT=pleyades_server_public_port
```
<small>"DB_ROOT_PWD" is optional (only needed if the Pleyades MySQL database is containerized)</small>

Institución de Educación Superior (IES) - Educatic Client

<small>"IES_CLIENT" is the acronym of the IES

Check the "ies.json" file to find the possible values for the client's short name</small>

<br>


###  web/.env
```env
JWT_KEY=ies_pleyades_jwt_secret
SESSION_KEY=ies_pleyades_session_secret_key
```


### api/.env
```env
MYSQL_SERVER=pleyades_db_server
MYSQL_SERVER_PORT=pleyades_db_server_port
MYSQL_USER=pleyades_db_user
MYSQL_PASSWORD=pleyades_db_password
MYSQL_DATABASE=pleyades_db_name

CLI_DB_SERVER=educatic_ies_clien.server.com
CLI_DB_USER=educatic_client_admin
CLI_DB_PASSWORD=educatic_client_admin_password
CLI_DB_NAME=educatic_ies_clien

JWT_KEY=ies_pleyades_jwt_secret
```


### Initialize database

If the MySQL database for Pleyades is not containerized;
please run the following .sql file before running the execution command
```
api/db/pleyades/sql/init.sql
```
If the database will be used in a Docker container, this process is automatic;

<br>

# Execution

Export the environment variables from /.env
```console
$ export $(cat .env | xargs)
```

Development mode 
```console
$ docker-compose up -d
```

Production mode 
```console
$ docker-compose -f docker-compose.prod.yml up -d
```

... including the containerized database
```console
$ docker-compose up db db-ies -d
$ docker-compose -f docker-compose.prod.yml up -d
```

Show running containers
```console
$ docker ps -a
```

<small>

Connect production containers (pleyades-api) with local development databases.

```console
$ docker-compose up -d
$ docker-compose -f docker-compose.prod.yml up -d
$ docker network connect pleyades-dev_dev-net pleyades-api
```

</small> 


# Stopping 


### Development containers

Stop 
```console
docker-compose stop
```

Remove 
```console
docker-compose rm -f
```

## Production Containers
Stop
```console
docker-compose -f docker-compose.prod.yml stop
```
Remove 
```console
docker-compose -f docker-compose.prod.yml rm -f
```

# Check errors (logs)

For container execution errors, check the Docker logs
```console
$ docker logs --tail 50 pleyades-web
$              ...         pleyades-api
$              ...         pleyades-nginx
```

For application errors, check the following logs 
```console
$ tail -n 50 api/logs/ERRORS.log
$     ...    api/logs/GENERALS.log
$     ...    web/logs/ERRORS.log
$     ...    web/logs/GENERALS.log
```


# Apply changes 
```console
$ git pull origin develop
$ docker-compose -f docker-compose.prod.yml stop &&
docker-compose -f docker-compose.prod.yml rm -f &&
docker-compose -f docker-compose.prod.yml up -d
````

# Remove Docker images for update 
Production
```console
$ docker-compose -f docker-compose.prod.yml down --rmi all
```
Development
```console
$ docker-compose down --rmi all
```

<br>
<br>



# Docker Installation (Engine)


### Desktop

Mac 
https://docs.docker.com/desktop/install/mac-install/

Linux
https://docs.docker.com/desktop/install/linux-install/

Windows
https://docs.docker.com/desktop/windows/install/

### Server (console)
#### Ubuntu

https://www.digitalocean.com/community/tutorials/como-instalar-y-usar-docker-en-ubuntu-18-04-1-es

https://www.digitalocean.com/community/tutorials/como-instalar-docker-compose-en-ubuntu-18-04-es

https://docs.docker.com/desktop/install/ubuntu/

```console
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt install docker.io
```

# Docker Compose Installation 
### Unix
```console
$ sudo curl -L https://github.com/docker/compose/releases/download/v2.4.1/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
```

### Windows
https://github.com/docker/compose/releases/download/v2.4.1/docker-compose-windows-x86_64.exe

Replace the docker-compose.exe in the following paths:

```console
C:\Program Files\Docker\Docker\resources\bin
C:\Program Files\Docker\Docker\resources\cli-plugins
C:\Program Files\Docker\cli-plugins
```

