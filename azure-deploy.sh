#!/bin/bash

# Script to deploy to Azure Container Apps with auto-scaling

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function for logging
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# --- Check if Azure CLI is installed ---
if ! command -v az &> /dev/null; then
    error "Azure CLI is not installed. Please install it: https://docs.microsoft.com/cli/azure/install-azure-cli"
fi

# ===============================================
# === CONFIGURATION VARIABLES ===
# ===============================================
RESOURCE_GROUP="db-repo"
LOCATION="westeurope"
ACR_NAME="dbrepolab2olya"
CONTAINER_APP_NAME="db-repo-app"
CONTAINER_APP_ENV="db-repo-env"
IMAGE_NAME="flask-rest-api"
IMAGE_TAG="latest"

# Database (must already exist in Azure)
DB_HOST="db-lab2.mysql.database.azure.com"
DB_USER="Olha"
DB_PASSWORD="Jksxrf189"
DB_NAME="db-lab2"
# ===============================================


log "Starting Azure deployment..."

# 1. Login to Azure (if needed)
log "Checking Azure authentication..."
az account show &> /dev/null || az login

# 2. Register required resource providers
log "Registering resource providers (Microsoft.App, Microsoft.OperationalInsights)..."
az provider register --namespace Microsoft.App --wait
az provider register --namespace Microsoft.OperationalInsights --wait
az provider register --namespace Microsoft.ContainerRegistry --wait
log "Resource providers registered."

# 3. Create Resource Group (if it doesn't exist)
log "Creating/checking Resource Group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION --output none

# 4. Check and create Azure Container Registry (ACR)
log "Checking for ACR: $ACR_NAME"
ACR_EXISTS=$(az acr show --name $ACR_NAME --resource-group $RESOURCE_GROUP 2>/dev/null)

if [ -z "$ACR_EXISTS" ]; then
    log "Creating new Azure Container Registry: $ACR_NAME"
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $ACR_NAME \
        --sku Basic \
        --admin-enabled true \
        --output none
    
    if [ $? -ne 0 ]; then
        error "Failed to create ACR. Check if the name '$ACR_NAME' is globally unique."
    fi
    log "ACR created successfully."
else
    log "ACR '$ACR_NAME' already exists, using existing."
    # Ensure admin is enabled
    az acr update --name $ACR_NAME --admin-enabled true --output none
fi

# 5. Login to ACR
log "Logging into Azure Container Registry..."
az acr login --name $ACR_NAME

if [ $? -ne 0 ]; then
    error "Failed to login to ACR. Check permissions."
fi

# 6. Build Docker image (for linux/amd64 platform used by Azure)
log "Building Docker image for linux/amd64 platform..."
# This uses the 'Dockerfile' in the current directory
docker buildx build --platform linux/amd64 -t ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    warning "Buildx failed, trying regular 'docker build'..."
    docker build --platform linux/amd64 -t ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} .
    
    if [ $? -ne 0 ]; then
        error "Failed to build Docker image. Check your Dockerfile."
    fi
fi
log "Docker image built successfully."

# 7. Push image to ACR
log "Pushing image to ${ACR_NAME}.azurecr.io..."
docker push ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG}

if [ $? -ne 0 ]; then
    error "Failed to push image to ACR."
fi
log "Image pushed successfully to ACR."

# 8. Get ACR credentials (username/password) for the Container App
log "Getting ACR credentials..."
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv 2>/dev/null)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv 2>/dev/null)

if [ -z "$ACR_USERNAME" ] || [ -z "$ACR_PASSWORD" ]; then
    error "Failed to get ACR credentials. Ensure admin-enabled=true for your ACR."
fi
log "Credentials obtained (User: $ACR_USERNAME)."

# 9. Create Container Apps Environment
log "Checking or creating Container Apps Environment: $CONTAINER_APP_ENV"
ENV_EXISTS=$(az containerapp env show --name $CONTAINER_APP_ENV --resource-group $RESOURCE_GROUP 2>/dev/null)

if [ -z "$ENV_EXISTS" ]; then
    log "Creating new Environment... (this may take a few minutes)"
    az containerapp env create \
        --name $CONTAINER_APP_ENV \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --output none
    
    if [ $? -ne 0 ]; then
        error "Failed to create Container Apps Environment."
    fi
    log "Environment created successfully."
else
    log "Environment '$CONTAINER_APP_ENV' already exists, using existing."
fi

# 10. Create (or update) the Container App
log "Checking for existing Container App: $CONTAINER_APP_NAME..."
APP_EXISTS=$(az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP 2>/dev/null)

if [ -n "$APP_EXISTS" ]; then
    warning "Container App '$CONTAINER_APP_NAME' already exists, deleting old one..."
    az containerapp delete \
        --name $CONTAINER_APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --yes \
        --output none
    log "Old Container App deleted."
fi

log "Creating new Container App: $CONTAINER_APP_NAME..."
az containerapp create \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINER_APP_ENV \
    --image ${ACR_NAME}.azurecr.io/${IMAGE_NAME}:${IMAGE_TAG} \
    --registry-server ${ACR_NAME}.azurecr.io \
    --registry-username "$ACR_USERNAME" \
    --registry-password "$ACR_PASSWORD" \
    --target-port 5000 \
    --ingress external \
    --min-replicas 1 \
    --max-replicas 10 \
    --cpu 0.5 \
    --memory 1.0Gi \
    --env-vars \
        DB_HOST="$DB_HOST" \
        DB_USER="$DB_USER" \
        DB_PASSWORD="$DB_PASSWORD" \
        DB_NAME="$DB_NAME" \
        PORT=5000 \
    --output none

if [ $? -ne 0 ]; then
    error "Failed to create Container App. Check error logs."
fi
log "Container App created successfully!"

# 11. Configure auto-scaling rules (CPU and Memory)
log "Configuring auto-scaling rules..."

log "Adding CPU scaling rule (> 70%)..."
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --scale-rule-name cpu-scaling \
    --scale-rule-type cpu \
    --scale-rule-metadata type=Utilization value=70 \
    --output none

log "Adding Memory scaling rule (> 80%)..."
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --scale-rule-name memory-scaling \
    --scale-rule-type memory \
    --scale-rule-metadata type=Utilization value=80 \
    --output none

log "Auto-scaling rules configured."

# 12. Get the deployed application URL
log "Getting Application URL..."
APP_URL=$(az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.configuration.ingress.fqdn -o tsv)

if [ -z "$APP_URL" ]; then
    warning "Could not automatically retrieve the Application URL."
    APP_URL="<failed to retrieve, check Azure Portal>"
fi

log "=========================================================="
log "                DEPLOYMENT COMPLETED!                     "
log "=========================================================="
log "Your Application URL: https://$APP_URL"
log "Swagger Documentation: https://$APP_URL/apidocs/"
log "----------------------------------------------------------"
log "Resource Group: $RESOURCE_GROUP"
log "Container Registry: ${ACR_NAME}.azurecr.io"
log "Container App: $CONTAINER_APP_NAME"
log "----------------------------------------------------------"
log "Auto-scaling configured:"
log "  - Min replicas: 1"
log "  - Max replicas: 10"
log "  - CPU rule: scale up @ >70% utilization"
log "  - Memory rule: scale up @ >80% utilization"
log "=========================================================="

# Save the URL to a file for easy access
echo "APP_URL=https://$APP_URL" > .env.azure
log "Application URL saved to .env.azure file."