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

/.env
```env
PLEYADES_IES_CLIENT=ies_client_short_name
PLEYADES_MYSQL_ROOT_PASSWORD=pleyades_db_root_password
```

Institución de Educación Superior (IES) - Cliente de Educatic
<br>
<small>Revisar el archivo ies.json para escoger el nombre corto del ies cliente</small>
<br>
<br>

web/.env
```env
JWT_KEY=ies_pleyades_jwt_secret
SESSION_KEY=ies_pleyades_session_secret_key
```


api/.env
```env
MYSQL_USER=pleyades_db_user
MYSQL_PASSWORD=pleyades_db_password
MYSQL_DATABASE=pleyades_db_name

CLI_DB_SERVER=educatic_ies_clien.server.com
CLI_DB_USER=educatic_client_admin
CLI_DB_PASSWORD=educatic_client_admin_password
CLI_DB_NAME=educatic_ies_clien

JWT_KEY=ies_pleyades_jwt_secret
```


# Ejecución

Exportar las variables de entorno /.env
```console
$ export $(cat .env | xargs)
```

Modo desarrollo 
```console
$ docker-compose up -d
```

Modo produccion (NGINX)
```console
$ docker-compose -f docker-compose.prod.yml up -d
```

# Instalación Docker 


## Maquina Desktop (Escritorio)

Mac 
https://docs.docker.com/desktop/install/mac-install/

Linux
https://docs.docker.com/desktop/install/linux-install/

Windows
https://docs.docker.com/desktop/windows/install/

## Maquina Server (consola)
Ubuntu

https://www.digitalocean.com/community/tutorials/como-instalar-y-usar-docker-en-ubuntu-18-04-1-es

https://www.digitalocean.com/community/tutorials/como-instalar-docker-compose-en-ubuntu-18-04-es

https://docs.docker.com/desktop/install/ubuntu/

```console
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt install docker.io
```

## Instalación Docker Compose 
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

