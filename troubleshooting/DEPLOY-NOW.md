# Fix 502 Error - Deploy Now

## Quick Deploy from Windows to Production Server

### Step 1: Upload Files to Server

From your **Windows machine**, open PowerShell or Git Bash and run:

```bash
# Replace 'user' and 'your-server' with your actual credentials
scp -r c:/work/vulnscan/* user@your-server:/opt/vulnscan/

# Or if you're using a specific key:
scp -i ~/.ssh/your-key.pem -r c:/work/vulnscan/* user@your-server:/opt/vulnscan/
```

### Step 2: SSH into Your Server

```bash
ssh user@your-server

# Or with key:
ssh -i ~/.ssh/your-key.pem user@your-server
```

### Step 3: Run the Fix Script

```bash
# Navigate to the project directory
cd /opt/vulnscan

# Make scripts executable
chmod +x diagnose.sh fix-502.sh

# Run the fix script (this will restart everything)
sudo ./fix-502.sh
```

The fix script will:
1. Stop all containers
2. Rebuild and restart them
3. Wait 30 seconds for containers to be ready
4. Test local access
5. Update nginx configuration
6. Restart nginx
7. Test the website

### If You Get Permission Errors

If the fix script fails with permission errors:

```bash
# Run these commands manually:

# 1. Stop and restart Docker containers
docker-compose down
docker-compose up -d --build

# 2. Wait 30 seconds
sleep 30

# 3. Test if containers are accessible
curl -I http://127.0.0.1:3001
curl http://127.0.0.1:8087/

# 4. Update nginx config
sudo cp nginx-scanner.conf /etc/nginx/sites-available/scanner
sudo ln -sf /etc/nginx/sites-available/scanner /etc/nginx/sites-enabled/scanner

# 5. Test nginx config
sudo nginx -t

# 6. Restart nginx
sudo systemctl restart nginx

# 7. Check status
sudo systemctl status nginx
```

### Step 4: Verify It's Working

Open your browser and go to: **https://scanner.keerthiyakkala.com**

You should see the VulnScan interface instead of a 502 error.

## If Still Getting 502 Error

Run the diagnostic script:

```bash
cd /opt/vulnscan
sudo ./diagnose.sh > diagnostic-output.txt

# View the output
cat diagnostic-output.txt
```

Then check these specific things:

### Check 1: Are containers actually running?

```bash
docker ps | grep vulnscan
```

You should see:
- `vulnscan-frontend` - Up
- `vulnscan-backend` - Up

If any show "Exited" or are missing:
```bash
docker logs vulnscan-frontend
docker logs vulnscan-backend
```

### Check 2: Can you access services locally?

```bash
curl -I http://127.0.0.1:3001
curl http://127.0.0.1:8087/
```

Both should return **200 OK**. If they fail:
- Containers might not be fully started (wait longer)
- Port conflicts (another service using the ports)
- Docker networking issue

### Check 3: What does nginx error log say?

```bash
sudo tail -50 /var/log/nginx/scanner.error.log
```

Look for:
- `connect() failed (111: Connection refused)` = Containers not accessible
- `connect() failed (113: No route to host)` = Firewall/networking issue
- `Permission denied` = SELinux blocking (see fix below)

### Check 4: SELinux Issues (CentOS/RHEL)

If you're on CentOS/RHEL and see permission errors:

```bash
# Check if SELinux is enforcing
getenforce

# If it returns "Enforcing", allow nginx to connect:
sudo setsebool -P httpd_can_network_connect 1

# Restart nginx
sudo systemctl restart nginx
```

### Check 5: Firewall

```bash
# Ubuntu/Debian
sudo ufw status

# CentOS/RHEL
sudo firewall-cmd --list-all

# Make sure ports 80, 443 are open for incoming
# Ports 3001, 8087 should NOT be open externally (only localhost)
```

## Common Issues and Solutions

| Symptom | Cause | Solution |
|---------|-------|----------|
| Containers keep restarting | Build failed or app crash | Check `docker logs vulnscan-frontend` and `docker logs vulnscan-backend` |
| `curl 127.0.0.1:3001` times out | Port binding issue | Change to `0.0.0.0:3001:80` in docker-compose.yml |
| `curl 127.0.0.1:3001` connection refused | Container not running | `docker-compose up -d --build` |
| Nginx says "Connection refused" | Containers not ready yet | Wait 60 seconds, then restart nginx |
| Works locally but 502 from internet | Nginx config issue | Verify `/etc/nginx/sites-enabled/scanner` exists |

## Still Need Help?

If none of the above works, gather this info:

```bash
cd /opt/vulnscan
sudo ./diagnose.sh > diagnostic.txt
cat diagnostic.txt
```

Share the output from `diagnostic.txt` for further troubleshooting.

## Alternative: Simplest Possible Test

If everything else fails, try this minimal test:

```bash
# Stop nginx temporarily
sudo systemctl stop nginx

# Test if you can access frontend directly (from your local machine)
# Open browser to: http://your-server-ip:3001

# If that works, the issue is nginx config
# If that doesn't work, the issue is Docker/containers
```
