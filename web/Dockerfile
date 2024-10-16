FROM python:3.12-slim

WORKDIR /app

# Update and install need packages
RUN apt-get -y update && apt-get -y upgrade

# Language configuration
RUN apt-get -y install locales locales-all tzdata
ARG LANGUAGE=es_MX.UTF-8

ENV LANGUAGE=$LANGUAGE
ENV LC_ALL=$LANGUAGE
ENV LC_CTYPE=$LANGUAGE

RUN locale-gen $LANGUAGE \
    && dpkg-reconfigure locales

# Timezone configuration
ARG TIMEZONE=America/Bogota
ENV TZ=$TIMEZONE
ENV TIME_ZONE=$TIMEZONE

# Upgrade pip, setuptools, and wheel
RUN pip install --upgrade pip setuptools wheel

# Copy resources
COPY . /app

# Install requirements
RUN pip install --no-cache-dir --no-build-isolation --upgrade --default-timeout=300 -r /app/requirements.txt

# Expose port
EXPOSE 80