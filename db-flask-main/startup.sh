#!/bin/bash

# Startup script для Azure App Service

echo "Starting Bus Management API on Azure App Service..."

# Отримати директорію скрипту
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Встановити змінні середовища для Azure
export PYTHONPATH="$SCRIPT_DIR"
export FLASK_APP="app.py"
export FLASK_ENV="production"

# Перевірити чи встановлено gunicorn
if ! command -v gunicorn &> /dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Створити директорію для логів якщо не існує
mkdir -p logs

# Перевірити чи існує app.py
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found in current directory"
    exit 1
fi

# Запуск Gunicorn для Azure App Service
echo "Starting Gunicorn..."
exec gunicorn --bind=0.0.0.0:8000 \
         --workers=2 \
         --timeout=600 \
         --access-logfile=- \
         --error-logfile=- \
         --log-level=info \
         --preload \
         --chdir="$SCRIPT_DIR" \
         app:app