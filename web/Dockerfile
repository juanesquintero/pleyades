FROM python:3.8-slim

WORKDIR /app

# Update and install need packages
RUN apt-get -y update &&  apt-get -y upgrade
RUN apt-get -y install locales locales-all tzdata

# Language configuration
ARG LANGUAGE=es_MX.UTF-8

ENV LANGUAGE=$LANGUAGE
ENV LC_ALL=$LANGUAGE
ENV LC_CTYPE=$LANGUAGE

RUN locale-gen $LANGUAGE
RUN dpkg-reconfigure locales

# Timezone configuration
ARG TIMEZONE=America/Bogota
ENV TZ=$TIMEZONE
ENV TIME_ZONE=$TIMEZONE

# Update pip
RUN pip install --upgrade pip

# Copy resources
COPY . /app

# Install requirements
RUN pip install --no-cache-dir --default-timeout=100 --upgrade -r /app/requirements.txt

# Expose port
EXPOSE 80
WORKDIR /app