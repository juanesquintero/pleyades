FROM python:3.8.3-slim

WORKDIR /app

# Update pip
RUN pip install --upgrade pip

# Copy resources
COPY ../ /app

# Install requirements
RUN pip install --no-cache-dir --upgrade -r /app/requirements-extra.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Expose port
EXPOSE 80
WORKDIR /app