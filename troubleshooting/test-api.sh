#!/bin/bash

echo "=================================="
echo "Testing API Endpoints"
echo "=================================="
echo ""

echo "1. Testing backend directly (should return JSON):"
echo "   curl http://127.0.0.1:8087/api/health"
curl http://127.0.0.1:8087/api/health
echo ""
echo ""

echo "2. Testing through nginx reverse proxy (should return JSON):"
echo "   curl https://scanner.keerthiyakkala.com/api/health"
curl https://scanner.keerthiyakkala.com/api/health
echo ""
echo ""

echo "3. Checking nginx config for /api/ location:"
echo "   sudo cat /etc/nginx/sites-available/scanner | grep -A 3 'location /api/'"
sudo cat /etc/nginx/sites-available/scanner | grep -A 3 'location /api/'
echo ""
echo ""

echo "=================================="
echo "Expected Results:"
echo "=================================="
echo "Test 1: Should show JSON with 'status' and 'demo_mode'"
echo "Test 2: Should show SAME JSON (not HTML)"
echo "Test 3: Should show 'proxy_pass http://api_backend;' WITHOUT trailing slash"
echo ""
