# PLEYADES 
(PLataforma de Exploración Y Analítica para la Desercion EStudiantil)

----------

<small>
</small>
<br>

# Montaje
Clonar el repositorio
```console
$ git clone https://gitlab.com/pleyades1/pleyades-educatic.git
```

Crear los .env desde los .env.template 

###  /.env
```env
IES_CLIENT=ies_client_short_name
DB_ROOT_PWD=pleyades_db_root_password
PUBLIC_PORT=pleyades_server_public_port
```
<small>DB_ROOT_PWD es opcional (es necesaria solo si la bd de Pleyades MySQL esta dockerizada)</small>


Institución de Educación Superior (IES) - Cliente de Educatic
<br>
<small>Revisar el archivo ies.json para escoger el nombre corto del ies cliente</small>
<br>
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

### Inicializar base de datos

Si la base de datos de mysql para Pleyades no se encuentra contenerizada;
por favor correr el siguiente archivo .sql, antes de correr el comando de ejecución 
```
api/db/pleyades/sql/init.sql
```
Si se usara la base de datos en Docker contenerizada, este proceso es automatico;

<br>

# Ejecución

Exportar las variables de entorno /.env
```console
$ export $(cat .env | xargs)
```

Modo desarrollo 
```console
$ docker-compose up -d
```

Modo producción (NGINX)
```console
$ docker-compose -f docker-compose.prod.yml up nginx -d
```

... incluyendo la base de datos dockerizada
```console
$ docker-compose -f docker-compose.prod.yml up -d
```

Evidenciar contenedores corriendo
```console
$ docker ps -a
```


# Detención 


### Contenedores de desarrollo

Parar 
```console
docker-compose stop
```

Eliminar 
```console
docker-compose rm -f
```

## Contenedores Productivos
Parar
```console
docker-compose -f docker-compose.prod.yml stop
```
Eliminar 
```console
docker-compose -f docker-compose.prod.yml rm -f
```

# Revisar errores (logs)

Errores en la ejecucion de contenedores, revisar los logs de Docker
```console
$ docker logs --tail 50 pleyades-web
$              ...         pleyades-api
$              ...         pleyades-nginx
```

Errores de la aplicacion corriendo, revisar los siguientes logs 
```console
$ tail -n 50 api/logs/ERRORS.log
$     ...    api/logs/GENERALS.log
$     ...    web/logs/ERRORS.log
$     ...    web/logs/GENERALS.log
```


# Aplicar cambios 
```console
$ git pull origin develop
$ docker-compose -f docker-compose.prod.yml stop
$ docker-compose -f docker-compose.prod.yml rm -f
$ docker-compose -f docker-compose.prod.yml up nginx -d
````

<br>
<br>



# Instalación Docker (Engine)


### Desktop (Escritorio)

Mac 
https://docs.docker.com/desktop/install/mac-install/

Linux
https://docs.docker.com/desktop/install/linux-install/

Windows
https://docs.docker.com/desktop/windows/install/

### Server (consola)
#### Ubuntu

https://www.digitalocean.com/community/tutorials/como-instalar-y-usar-docker-en-ubuntu-18-04-1-es

https://www.digitalocean.com/community/tutorials/como-instalar-docker-compose-en-ubuntu-18-04-es

https://docs.docker.com/desktop/install/ubuntu/

```console
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt install docker.io
```

# Instalación Docker Compose 
### Unix
```console
$ sudo curl -L https://github.com/docker/compose/releases/download/v2.4.1/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
```

### Windows
https://github.com/docker/compose/releases/download/v2.4.1/docker-compose-windows-x86_64.exe

Remplazar el docker-compose.exe de las siguientes rutas:

```console
C:\Program Files\Docker\Docker\resources\bin
C:\Program Files\Docker\Docker\resources\cli-plugins
C:\Program Files\Docker\cli-plugins
```

