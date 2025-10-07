#!/bin/bash

# Azure VM Setup Script
# This script helps set up the VM for Flask app deployment

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

print_status "Setting up Azure VM for Flask app deployment..."

# Test SSH connection
if ! ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no $VM_USERNAME@$VM_HOST "echo 'SSH connection successful'"; then
    print_error "Cannot connect to VM. Please check SSH connection first."
    exit 1
fi

# Setup VM
ssh $VM_USERNAME@$VM_HOST << EOF
echo "🔧 Setting up VM for Flask deployment..."

# Update system
sudo apt update

# Install Python 3.9 and pip
sudo apt install -y python3.9 python3.9-venv python3-pip

# Install system dependencies
sudo apt install -y nginx supervisor

# Create deployment directory
mkdir -p $DEPLOY_PATH

# Create systemd service file
sudo tee /etc/systemd/system/bus-management-api.service > /dev/null << 'SERVICE_EOF'
[Unit]
Description=Bus Management API
After=network.target

[Service]
Type=simple
User=$VM_USERNAME
WorkingDirectory=$DEPLOY_PATH
Environment=PATH=$DEPLOY_PATH/.venv/bin
ExecStart=$DEPLOY_PATH/.venv/bin/gunicorn --bind=0.0.0.0:$APP_PORT --workers=2 --timeout=600 --access-logfile=- --error-logfile=- app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Create nginx configuration
sudo tee /etc/nginx/sites-available/bus-management-api > /dev/null << 'NGINX_EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX_EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/bus-management-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Enable services
sudo systemctl enable bus-management-api
sudo systemctl enable nginx

echo "✅ VM setup completed!"
echo "Services configured:"
echo "- bus-management-api.service (systemd)"
echo "- nginx (reverse proxy)"
echo ""
echo "Next steps:"
echo "1. Deploy your application using deploy-to-vm.sh"
echo "2. Start the service: sudo systemctl start bus-management-api"
echo "3. Check status: sudo systemctl status bus-management-api"
EOF

print_status "VM setup completed!"
print_warning "Don't forget to:"
echo "1. Open port 80 in Azure VM firewall"
echo "2. Configure your domain DNS to point to VM IP"
echo "3. Set up SSL certificate if needed"
