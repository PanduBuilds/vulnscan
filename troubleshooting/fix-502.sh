#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================"
echo "VulnScan 502 Error Fix Script"
echo "========================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if docker-compose exists, otherwise use docker compose
DOCKER_COMPOSE="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
    echo -e "${YELLOW}Note: Using 'docker compose' instead of 'docker-compose'${NC}"
fi

echo -e "${YELLOW}Step 1: Stopping all containers...${NC}"
$DOCKER_COMPOSE down 2>/dev/null || true
echo -e "${GREEN}✓ Containers stopped${NC}"
echo ""

echo -e "${YELLOW}Step 2: Removing old containers and networks...${NC}"
docker container prune -f
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

echo -e "${YELLOW}Step 3: Building containers (no cache)...${NC}"
$DOCKER_COMPOSE build --no-cache
echo -e "${GREEN}✓ Build complete${NC}"
echo ""

echo -e "${YELLOW}Step 4: Starting containers...${NC}"
$DOCKER_COMPOSE up -d
echo -e "${GREEN}✓ Containers started${NC}"
echo ""

echo -e "${YELLOW}Step 5: Waiting for containers to be ready (30 seconds)...${NC}"
for i in {30..1}; do
    echo -ne "\r${BLUE}Waiting: $i seconds remaining...${NC}"
    sleep 1
done
echo ""
echo -e "${GREEN}✓ Wait complete${NC}"
echo ""

echo -e "${YELLOW}Step 6: Checking container status...${NC}"
docker ps | grep vulnscan
echo ""

echo -e "${YELLOW}Step 7: Testing local access...${NC}"
echo "Testing frontend (http://127.0.0.1:3001):"
if timeout 5 curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001 | grep -q "200"; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
else
    echo -e "${RED}✗ Frontend is NOT accessible${NC}"
    echo "Frontend logs:"
    docker logs vulnscan-frontend --tail 10
fi
echo ""

echo "Testing backend (http://127.0.0.1:8087/):"
if timeout 5 curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8087/ | grep -q "200"; then
    echo -e "${GREEN}✓ Backend is accessible${NC}"
else
    echo -e "${RED}✗ Backend is NOT accessible${NC}"
    echo "Backend logs:"
    docker logs vulnscan-backend --tail 10
fi
echo ""

echo -e "${YELLOW}Step 8: Checking if nginx config exists...${NC}"
if [ -f "nginx-scanner.conf" ]; then
    echo -e "${GREEN}✓ nginx-scanner.conf found${NC}"

    echo -e "${YELLOW}Step 9: Updating nginx configuration...${NC}"
    sudo cp nginx-scanner.conf /etc/nginx/sites-available/scanner

    # Create symlink if it doesn't exist
    if [ ! -L /etc/nginx/sites-enabled/scanner ]; then
        sudo ln -s /etc/nginx/sites-available/scanner /etc/nginx/sites-enabled/scanner
    fi
    echo -e "${GREEN}✓ Nginx config updated${NC}"
    echo ""

    # Remove default config that might conflict
    if [ -f /etc/nginx/sites-enabled/default ]; then
        echo -e "${YELLOW}Removing default nginx config...${NC}"
        sudo rm -f /etc/nginx/sites-enabled/default
    fi

    echo -e "${YELLOW}Step 10: Testing nginx configuration...${NC}"
    if sudo nginx -t; then
        echo -e "${GREEN}✓ Nginx config is valid${NC}"
    else
        echo -e "${RED}✗ Nginx config has errors${NC}"
        exit 1
    fi
    echo ""

    echo -e "${YELLOW}Step 11: Restarting nginx...${NC}"
    sudo systemctl restart nginx

    if sudo systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✓ Nginx restarted successfully${NC}"
    else
        echo -e "${RED}✗ Nginx failed to start${NC}"
        echo "Checking nginx status:"
        sudo systemctl status nginx
        exit 1
    fi
else
    echo -e "${RED}✗ nginx-scanner.conf not found in current directory${NC}"
    echo "Please make sure you're running this script from the vulnscan directory"
    exit 1
fi
echo ""

echo "========================================"
echo -e "${GREEN}Fix script complete!${NC}"
echo "========================================"
echo ""
echo -e "${BLUE}Now testing the website...${NC}"
echo ""

# Test the website
echo "Testing https://scanner.keerthiyakkala.com:"
HTTP_CODE=$(timeout 10 curl -s -o /dev/null -w "%{http_code}" -k https://scanner.keerthiyakkala.com 2>&1)

if [[ "$HTTP_CODE" == "200" ]]; then
    echo -e "${GREEN}✓✓✓ SUCCESS! Website is now accessible${NC}"
    echo "Status code: $HTTP_CODE"
elif [[ "$HTTP_CODE" == "502" ]]; then
    echo -e "${RED}✗ Still getting 502 error${NC}"
    echo ""
    echo "Additional troubleshooting needed. Check:"
    echo "1. Can you access http://127.0.0.1:3001 directly on the server?"
    echo "2. Check nginx error log: sudo tail -50 /var/log/nginx/scanner.error.log"
    echo "3. Check if SELinux is blocking: getenforce"
else
    echo -e "${YELLOW}⚠ Got unexpected status: $HTTP_CODE${NC}"
fi
echo ""
echo "You can also check:"
echo "  - Frontend: http://127.0.0.1:3001"
echo "  - Backend: http://127.0.0.1:8087/"
echo "  - Nginx logs: sudo tail -f /var/log/nginx/scanner.error.log"
