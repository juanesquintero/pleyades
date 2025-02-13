FROM python:3.13.2-slim AS production

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

WORKDIR /app

# Expose port
EXPOSE 80


#######################  DEVELOPMENT  #######################
FROM production AS development

ENV PYTHONUNBUFFERED=1
ENV FLASK_DEBUG=1
ENV FLASK_APP=run.py
ENV TEMPLATES_AUTO_RELOAD=1

RUN pip install --no-cache-dir --upgrade  -r /app/requirements-dev.txt
