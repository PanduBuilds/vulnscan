# FINAL FIX - Copy and Paste These Commands

## Step 1: Upload Files to Production Server

From your **Windows machine**, run this in PowerShell or Git Bash:

```bash
# Replace 'user@your-server' with your actual server details
scp -r c:/work/vulnscan/* user@your-server:/opt/vulnscan/
```

## Step 2: SSH to Your Server

```bash
ssh user@your-server
```

## Step 3: Copy and Paste This Entire Block

```bash
# Navigate to project
cd /opt/vulnscan

# Stop everything
docker-compose down 2>/dev/null || true

# Remove old images to force rebuild
docker-compose build --no-cache

# Start containers
docker-compose up -d

# Wait for containers to be ready
echo "Waiting 30 seconds for containers to start..."
sleep 30

# Check container status
echo "=== Container Status ==="
docker ps | grep vulnscan

# Test local access
echo ""
echo "=== Testing Local Access ==="
echo "Frontend:"
curl -I http://127.0.0.1:3001 2>&1 | head -5
echo ""
echo "Backend:"
curl -s http://127.0.0.1:8087/ 2>&1 | head -5

# Update nginx config
echo ""
echo "=== Updating Nginx Config ==="
sudo cp nginx-scanner.conf /etc/nginx/sites-available/scanner
sudo ln -sf /etc/nginx/sites-available/scanner /etc/nginx/sites-enabled/scanner

# Remove default config if it conflicts
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx config
echo ""
echo "=== Testing Nginx Config ==="
sudo nginx -t

# Restart nginx
echo ""
echo "=== Restarting Nginx ==="
sudo systemctl restart nginx
sudo systemctl status nginx --no-pager -l

# Final test
echo ""
echo "=== Testing Website ==="
curl -I https://scanner.keerthiyakkala.com 2>&1 | head -10

echo ""
echo "=== DONE ==="
echo "Check https://scanner.keerthiyakkala.com in your browser"
```

## If You See Errors

### Error: "docker-compose: command not found"

Try with docker compose (no hyphen):
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Error: "Address already in use"

Another process is using the ports:
```bash
# Find what's using port 3001
sudo lsof -i :3001
sudo lsof -i :8087

# Kill those processes or change ports in docker-compose.yml
```

### Error: "Permission denied" in nginx logs

SELinux is blocking (CentOS/RHEL):
```bash
sudo setsebool -P httpd_can_network_connect 1
sudo systemctl restart nginx
```

### Error: Containers keep restarting

Check the logs:
```bash
docker logs vulnscan-frontend --tail 50
docker logs vulnscan-backend --tail 50
```

### Still Getting 502 After All Commands

Try accessing the frontend directly without nginx:
```bash
# Temporarily open port 3001 in firewall
sudo ufw allow 3001   # Ubuntu
# OR
sudo firewall-cmd --add-port=3001/tcp --permanent && sudo firewall-cmd --reload  # CentOS

# Then try accessing from your browser: http://your-server-ip:3001
```

If that works, the issue is nginx. If it doesn't work, the issue is Docker containers.

## Alternative: Use Port 0.0.0.0 Instead

If 127.0.0.1 binding doesn't work, edit docker-compose.yml on the server:

```bash
cd /opt/vulnscan

# Change 127.0.0.1 to 0.0.0.0
sed -i 's/127.0.0.1:3001:80/0.0.0.0:3001:80/g' docker-compose.yml
sed -i 's/127.0.0.1:8087:8080/0.0.0.0:8087:8080/g' docker-compose.yml
sed -i 's/127.0.0.1:8086:80/0.0.0.0:8086:80/g' docker-compose.yml

# Restart containers
docker-compose down
docker-compose up -d

# Wait and test
sleep 20
curl -I http://localhost:3001
```

## Quick Verification Checklist

Run these to verify everything:

```bash
# ✓ Containers running?
docker ps | grep vulnscan | grep Up

# ✓ Ports listening?
sudo netstat -tlnp | grep -E '3001|8087'

# ✓ Nginx config valid?
sudo nginx -t

# ✓ Nginx running?
sudo systemctl is-active nginx

# ✓ Can access locally?
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3001

# ✓ Can access via domain?
curl -s -o /dev/null -w "%{http_code}" https://scanner.keerthiyakkala.com
```

All should return success/200.
