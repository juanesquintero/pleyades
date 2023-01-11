<h1>PLEYADES</h1>
(PLataforma de Exploración Y Analítica para la Desercion EStudiantil)

----------

<br>

## Run
Development mode 
```
$ docker-compose up -d
```

Prodction
```
$ docker-compose -f docker-compose.prod.yml up -d
```

## Docker 
Pasos para instalar docker 

### Mac & Linux

Mac
https://docs.docker.com/desktop/install/mac-install/

Linux
https://docs.docker.com/desktop/install/linux-install/

Docker Compose
```console
sudo curl -L https://github.com/docker/compose/releases/download/v2.4.1/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
```

Ubuntu
https://www.digitalocean.com/community/tutorials/como-instalar-y-usar-docker-en-ubuntu-18-04-1-es

https://www.digitalocean.com/community/tutorials/como-instalar-docker-compose-en-ubuntu-18-04-es

https://docs.docker.com/desktop/install/ubuntu/
sudo apt-get update
sudo apt-get upgrade
sudo apt install docker.io

### Windows 10

Instalar docker desktop desde:
https://docs.docker.com/desktop/windows/install/

Descargar docker-compose v2.4.1:
https://github.com/docker/compose/releases/download/v2.4.1/docker-compose-windows-x86_64.exe


...y remplazar el docker-compose.exe de las siguientes rutas:

```console
C:\Program Files\Docker\Docker\resources\bin

C:\Program Files\Docker\Docker\resources\cli-plugins

C:\Program Files\Docker\cli-plugins
```

