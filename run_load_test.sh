#!/bin/bash


GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}--- Azure App Load Tester ---${NC}"

if [ -n "$1" ]; then
    URL=$1
else
    if [ -f ".env.azure" ]; then
        source .env.azure
        URL=$APP_URL
    fi
    
    if [ -z "$URL" ]; then
        echo -e "${YELLOW}Please enter the URL to test (e.g., https://app.azure.com/buses):${NC}"
        read URL
    fi
fi

if [ -n "$2" ]; then
    THREADS=$2
else
    echo -e "${YELLOW}Enter number of threads (default: 20):${NC}"
    read THREADS
    if [ -z "$THREADS" ]; then
        THREADS=20
    fi
fi

if [ -n "$3" ]; then
    DURATION=$3
else
    echo -e "${YELLOW}Enter duration in seconds (default: 300):${NC}"
    read DURATION
    if [ -z "$DURATION" ]; then
        DURATION=300
    fi
fi

if [ -z "$URL" ]; then
    echo -e "\n${RED}ERROR: URL cannot be empty.${NC}"
    exit 1
fi

echo -e "\n${GREEN}Starting test with the following parameters:${NC}"
echo "URL: $URL"
echo "Threads: $THREADS"
echo "Duration: $DURATION seconds"
echo -e "Press Ctrl+C to stop the test early.\n"

python load_test.py --url "$URL" --threads "$THREADS" --duration "$DURATION"