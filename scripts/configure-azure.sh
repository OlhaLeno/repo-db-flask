#!/bin/bash

# Azure App Service Configuration Script
# This script helps configure Azure App Service settings

set -e

# Configuration
APP_NAME="${AZURE_WEBAPP_NAME:-your-app-name}"
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-your-resource-group}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to set environment variables
set_env_var() {
    local key=$1
    local value=$2
    
    if [ -z "$value" ]; then
        print_warning "Value for $key is empty. Skipping..."
        return
    fi
    
    print_status "Setting $key..."
    az webapp config appsettings set \
        --name "$APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --settings "$key=$value" \
        --output none
}

# Database configuration
echo "🔧 Configuring Azure App Service..."

# Set database connection
if [ -n "$DB_HOST" ]; then
    set_env_var "DB_HOST" "$DB_HOST"
fi

if [ -n "$DB_USER" ]; then
    set_env_var "DB_USER" "$DB_USER"
fi

if [ -n "$DB_PASSWORD" ]; then
    set_env_var "DB_PASSWORD" "$DB_PASSWORD"
fi

if [ -n "$DB_NAME" ]; then
    set_env_var "DB_NAME" "$DB_NAME"
fi

if [ -n "$DB_PORT" ]; then
    set_env_var "DB_PORT" "$DB_PORT"
fi

# Security
if [ -n "$SECRET_KEY" ]; then
    set_env_var "SECRET_KEY" "$SECRET_KEY"
fi

# Application settings
set_env_var "FLASK_APP" "app.py"
set_env_var "FLASK_ENV" "production"
set_env_var "PYTHONPATH" "/home/site/wwwroot"

print_status "Configuration completed!"
print_status "You can view your app at: https://${APP_NAME}.azurewebsites.net"
