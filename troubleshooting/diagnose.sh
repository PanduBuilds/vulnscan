#!/bin/bash

echo "========================================"
echo "VulnScan 502 Error Diagnostic Script"
echo "========================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}[1/8] Checking Docker installation...${NC}"
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker is installed${NC}"
    docker --version
else
    echo -e "${RED}✗ Docker is NOT installed${NC}"
fi
echo ""

echo -e "${YELLOW}[2/8] Checking Docker containers status...${NC}"
docker ps -a | grep vulnscan
echo ""

echo -e "${YELLOW}[3/8] Checking if ports are listening...${NC}"
echo "Port 3001 (Frontend):"
sudo netstat -tlnp | grep 3001 || echo "Not listening"
echo ""
echo "Port 8087 (Backend):"
sudo netstat -tlnp | grep 8087 || echo "Not listening"
echo ""

echo -e "${YELLOW}[4/8] Testing local access to frontend...${NC}"
timeout 5 curl -I http://127.0.0.1:3001 2>&1 | head -10
echo ""

echo -e "${YELLOW}[5/8] Testing local access to backend...${NC}"
timeout 5 curl http://127.0.0.1:8087/ 2>&1 | head -10
echo ""

echo -e "${YELLOW}[6/8] Checking Docker logs - Frontend (last 20 lines)...${NC}"
docker logs vulnscan-frontend --tail 20 2>&1 || echo "Frontend container not found"
echo ""

echo -e "${YELLOW}[7/8] Checking Docker logs - Backend (last 20 lines)...${NC}"
docker logs vulnscan-backend --tail 20 2>&1 || echo "Backend container not found"
echo ""

echo -e "${YELLOW}[8/8] Checking Nginx error logs (last 30 lines)...${NC}"
if [ -f /var/log/nginx/scanner.error.log ]; then
    sudo tail -30 /var/log/nginx/scanner.error.log
else
    echo "Nginx error log not found at /var/log/nginx/scanner.error.log"
    echo "Checking main nginx error log:"
    sudo tail -30 /var/log/nginx/error.log
fi
echo ""

echo "========================================"
echo -e "${GREEN}Diagnostic complete!${NC}"
echo "========================================"
echo ""
echo "Common issues to look for:"
echo "  - Containers show 'Exited' status"
echo "  - Ports not listening (no output for netstat)"
echo "  - curl commands timeout or show 'Connection refused'"
echo "  - Nginx logs show 'upstream' errors"
echo ""
echo "Save this output and share it if you need further help."
