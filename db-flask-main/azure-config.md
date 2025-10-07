# Azure App Service Configuration
# This file contains configuration for Azure App Service deployment

# Python Runtime
PYTHON_VERSION=3.9

# Startup Configuration
STARTUP_COMMAND=startup.sh

# Application Settings
FLASK_APP=app.py
FLASK_ENV=production
PYTHONPATH=/home/site/wwwroot

# Database Configuration
# These should be set as environment variables in Azure Portal:
# - DB_HOST: Your Azure MySQL server hostname
# - DB_USER: Database username
# - DB_PASSWORD: Database password
# - DB_NAME: Database name
# - DB_PORT: Database port (default: 3306)

# Security
# Set SECRET_KEY as environment variable in Azure Portal

# Performance Settings
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=600
GUNICORN_BIND=0.0.0.0:8000

# Logging
LOG_LEVEL=INFO
