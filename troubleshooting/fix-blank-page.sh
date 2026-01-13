#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Fix Blank Page Issue"
echo "========================================"
echo ""

cd "$(dirname "$0")"

echo -e "${YELLOW}Stopping frontend container...${NC}"
docker stop vulnscan-frontend 2>/dev/null || true
docker rm vulnscan-frontend 2>/dev/null || true

echo -e "${YELLOW}Rebuilding frontend container (no cache)...${NC}"
docker-compose build --no-cache frontend

echo -e "${YELLOW}Starting frontend container...${NC}"
docker-compose up -d frontend

echo -e "${YELLOW}Waiting 10 seconds for container to start...${NC}"
sleep 10

echo ""
echo -e "${GREEN}Testing...${NC}"
echo ""

echo "1. Testing index.html:"
curl -I http://127.0.0.1:3001/ 2>&1 | head -5

echo ""
echo "2. Testing assets (checking if any JS file exists):"
# Get the actual asset filename from the built index.html
ASSET=$(docker exec vulnscan-frontend ls /usr/share/nginx/html/assets/*.js 2>/dev/null | head -1 | xargs basename)
if [ -n "$ASSET" ]; then
    echo "Found asset: $ASSET"
    curl -I http://127.0.0.1:3001/assets/$ASSET 2>&1 | head -5
else
    echo "No JS assets found in /usr/share/nginx/html/assets/"
fi

echo ""
echo "3. Listing files in container:"
docker exec vulnscan-frontend ls -la /usr/share/nginx/html/
echo ""
docker exec vulnscan-frontend ls -la /usr/share/nginx/html/assets/ 2>/dev/null || echo "No assets directory"

echo ""
echo -e "${GREEN}Done! Check https://scanner.keerthiyakkala.com${NC}"
echo ""
echo "If still blank, run:"
echo "  docker logs vulnscan-frontend"
