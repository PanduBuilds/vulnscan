#!/bin/bash

# Complete fix script for blank page + 404 + CORS issues

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "================================================"
echo "Complete Fix: Blank Page + 404 + CORS"
echo "================================================"
echo ""

cd "$(dirname "$0")"

# Check if docker-compose exists
DOCKER_COMPOSE="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
fi

echo -e "${YELLOW}Step 1: Stopping all containers...${NC}"
$DOCKER_COMPOSE down
echo -e "${GREEN}✓ Stopped${NC}"
echo ""

echo -e "${YELLOW}Step 2: Removing old Docker images (to force rebuild)...${NC}"
docker rmi vulnscan-frontend vulnscan-backend 2>/dev/null || true
echo -e "${GREEN}✓ Cleaned${NC}"
echo ""

echo -e "${YELLOW}Step 3: Building containers with no cache...${NC}"
$DOCKER_COMPOSE build --no-cache
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Build failed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Built${NC}"
echo ""

echo -e "${YELLOW}Step 4: Starting containers...${NC}"
$DOCKER_COMPOSE up -d
echo -e "${GREEN}✓ Started${NC}"
echo ""

echo -e "${YELLOW}Step 5: Waiting 30 seconds for containers to be ready...${NC}"
for i in {30..1}; do
    echo -ne "\rWaiting: $i seconds...  "
    sleep 1
done
echo ""
echo -e "${GREEN}✓ Ready${NC}"
echo ""

echo -e "${YELLOW}Step 6: Verifying container status...${NC}"
docker ps | grep vulnscan
echo ""

echo -e "${YELLOW}Step 7: Testing frontend container locally...${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/)
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ Frontend index.html returns 200${NC}"
else
    echo -e "${RED}✗ Frontend returns $HTTP_CODE (should be 200)${NC}"
    echo "Logs:"
    docker logs vulnscan-frontend --tail 20
fi
echo ""

echo -e "${YELLOW}Step 8: Testing frontend assets...${NC}"
# Get first JS asset filename
ASSET=$(docker exec vulnscan-frontend sh -c "ls /usr/share/nginx/html/assets/*.js 2>/dev/null | head -1" | xargs basename 2>/dev/null)
if [ -n "$ASSET" ]; then
    echo "Testing asset: $ASSET"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001/assets/$ASSET)
    if [ "$HTTP_CODE" == "200" ]; then
        echo -e "${GREEN}✓ Assets return 200${NC}"
    else
        echo -e "${RED}✗ Asset returns $HTTP_CODE (should be 200)${NC}"
        echo "Checking nginx config in container:"
        docker exec vulnscan-frontend cat /etc/nginx/conf.d/default.conf | grep -A 5 "location ~"
    fi
else
    echo -e "${RED}✗ No JS assets found in container${NC}"
    echo "Contents of /usr/share/nginx/html:"
    docker exec vulnscan-frontend ls -la /usr/share/nginx/html/
    echo "Contents of /usr/share/nginx/html/assets:"
    docker exec vulnscan-frontend ls -la /usr/share/nginx/html/assets/ 2>/dev/null || echo "No assets directory!"
fi
echo ""

echo -e "${YELLOW}Step 9: Testing backend API...${NC}"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8087/)
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ Backend API returns 200${NC}"
else
    echo -e "${RED}✗ Backend returns $HTTP_CODE${NC}"
    echo "Logs:"
    docker logs vulnscan-backend --tail 20
fi
echo ""

echo -e "${YELLOW}Step 10: Updating host nginx configuration...${NC}"
if [ -f "nginx-scanner.conf" ]; then
    sudo cp nginx-scanner.conf /etc/nginx/sites-available/scanner
    sudo ln -sf /etc/nginx/sites-available/scanner /etc/nginx/sites-enabled/scanner
    sudo rm -f /etc/nginx/sites-enabled/default
    echo -e "${GREEN}✓ Nginx config updated${NC}"
else
    echo -e "${RED}✗ nginx-scanner.conf not found${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 11: Testing nginx configuration...${NC}"
if sudo nginx -t 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✓ Nginx config is valid${NC}"
else
    echo -e "${RED}✗ Nginx config has errors${NC}"
    sudo nginx -t
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 12: Restarting nginx...${NC}"
sudo systemctl restart nginx
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx restarted${NC}"
else
    echo -e "${RED}✗ Nginx failed to start${NC}"
    sudo systemctl status nginx --no-pager
    exit 1
fi
echo ""

echo "================================================"
echo -e "${GREEN}Fix Complete!${NC}"
echo "================================================"
echo ""
echo "Test your website: https://scanner.keerthiyakkala.com"
echo ""
echo -e "${YELLOW}If still having issues, check:${NC}"
echo "1. Browser console (F12) for specific errors"
echo "2. docker logs vulnscan-frontend"
echo "3. docker logs vulnscan-backend"
echo "4. sudo tail -50 /var/log/nginx/scanner.error.log"
echo ""
echo "Run diagnostics:"
echo "  ./diagnose.sh"
