#!/bin/bash

# Startup script для Azure VM (Linux)

echo "Starting Bus Management API on Azure..."

# Отримати директорію скрипту
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Активувати віртуальне середовище
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "ERROR: Virtual environment not found!"
    echo "Please create it first: python3 -m venv .venv"
    exit 1
fi

# Перевірити чи встановлено gunicorn
if ! command -v gunicorn &> /dev/null; then
    echo "ERROR: gunicorn not found!"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Запуск Gunicorn з віртуального середовища
echo "Starting Gunicorn..."
exec gunicorn --bind=0.0.0.0:8000 \
         --workers=4 \
         --timeout=600 \
         --access-logfile=- \
         --error-logfile=- \
         app:app

