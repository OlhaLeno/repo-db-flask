#!/bin/bash

# Azure VM Deployment Script
# This script helps deploy Flask app to existing Azure VM

set -e

# Configuration
VM_HOST="${VM_HOST:-your-vm-ip}"
VM_USERNAME="${VM_USERNAME:-azureuser}"
DEPLOY_PATH="${DEPLOY_PATH:-/home/azureuser/bus-management-api}"
APP_PORT="${APP_PORT:-8000}"

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

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa ]; then
    print_warning "SSH key not found. Generating new key..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    print_status "SSH key generated. Add the public key to your VM:"
    cat ~/.ssh/id_rsa.pub
    echo ""
    print_warning "Run this command on your VM to add the key:"
    echo "mkdir -p ~/.ssh && echo '$(cat ~/.ssh/id_rsa.pub)' >> ~/.ssh/authorized_keys"
    exit 1
fi

print_status "Deploying to Azure VM: $VM_HOST"

# Test SSH connection
if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $VM_USERNAME@$VM_HOST "echo 'SSH connection successful'"; then
    print_error "Cannot connect to VM. Please check:"
    echo "1. VM is running"
    echo "2. SSH port (22) is open"
    echo "3. SSH key is added to VM"
    echo "4. VM_HOST and VM_USERNAME are correct"
    exit 1
fi

# Create deployment directory
print_status "Creating deployment directory..."
ssh $VM_USERNAME@$VM_HOST "mkdir -p $DEPLOY_PATH"

# Copy files
print_status "Copying files to VM..."
scp -r db-flask-main/* $VM_USERNAME@$VM_HOST:$DEPLOY_PATH/

# Deploy on VM
print_status "Deploying application on VM..."
ssh $VM_USERNAME@$VM_HOST << EOF
cd $DEPLOY_PATH

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Make startup script executable
chmod +x startup.sh

# Stop existing application if running
pkill -f "gunicorn.*app:app" || echo "No existing application found"

# Start application
echo "Starting application..."
nohup ./startup.sh > app.log 2>&1 &

# Wait a moment and check if it's running
sleep 5
if pgrep -f "gunicorn.*app:app" > /dev/null; then
    echo "✅ Application started successfully"
    echo "Application is running on port $APP_PORT"
else
    echo "❌ Application failed to start. Check app.log for details"
    exit 1
fi
EOF

print_status "Deployment completed!"
print_status "Application URL: http://$VM_HOST:$APP_PORT"
print_status "Health check: http://$VM_HOST:$APP_PORT/healthz"
print_status "API docs: http://$VM_HOST:$APP_PORT/apidocs"
