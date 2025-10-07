#!/bin/bash

# Azure App Service Deployment Script
# This script helps with Azure App Service deployment

set -e

echo "🚀 Starting Azure App Service deployment..."

# Configuration
APP_NAME="${AZURE_WEBAPP_NAME:-your-app-name}"
RESOURCE_GROUP="${AZURE_RESOURCE_GROUP:-your-resource-group}"
LOCATION="${AZURE_LOCATION:-East US}"
SKU="${AZURE_SKU:-F1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it first."
    echo "Visit: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    print_warning "Not logged in to Azure. Please run 'az login' first."
    exit 1
fi

print_status "Creating Azure App Service..."

# Create App Service Plan
print_status "Creating App Service Plan..."
az appservice plan create \
    --name "${APP_NAME}-plan" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --sku "$SKU" \
    --is-linux

# Create Web App
print_status "Creating Web App..."
az webapp create \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --plan "${APP_NAME}-plan" \
    --runtime "PYTHON|3.9"

# Configure app settings
print_status "Configuring app settings..."
az webapp config appsettings set \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
        FLASK_APP="app.py" \
        FLASK_ENV="production" \
        PYTHONPATH="/home/site/wwwroot" \
        SCM_DO_BUILD_DURING_DEPLOYMENT="true"

print_status "Deployment configuration completed!"
print_status "App URL: https://${APP_NAME}.azurewebsites.net"
print_warning "Don't forget to:"
echo "1. Set your database connection strings in Azure Portal"
echo "2. Set your SECRET_KEY in Azure Portal"
echo "3. Configure GitHub secrets for deployment"
