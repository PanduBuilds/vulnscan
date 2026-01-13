# Complete Fix for Blank Page + 404 + CORS Issues

## Issues Found

1. **404 for assets** - Frontend container nginx fix may not be deployed
2. **CORS errors** - Backend CORS list doesn't include all variations of your domain
3. **Host nginx might be interfering** - Reverse proxy needs proper headers

## Fixes Required

### Fix 1: Ensure Frontend nginx.conf is Deployed

The fix was made to `frontend/nginx.conf` but container needs rebuild.

### Fix 2: Update Backend CORS

Backend only allows specific origins. Need to add more variations.

### Fix 3: Update Host Nginx Reverse Proxy

Add explicit handling for assets to avoid issues.

## Complete Fix Script

Upload all files and run this on your server:

```bash
#!/bin/bash

cd /opt/vulnscan

echo "=== Step 1: Stopping containers ==="
docker-compose down

echo "=== Step 2: Rebuilding (no cache) ==="
docker-compose build --no-cache

echo "=== Step 3: Starting containers ==="
docker-compose up -d

echo "=== Step 4: Waiting 30 seconds ==="
sleep 30

echo "=== Step 5: Testing containers locally ==="
echo "Frontend:"
curl -I http://127.0.0.1:3001/ | head -5
echo ""
echo "Backend:"
curl http://127.0.0.1:8087/ | head -5
echo ""

echo "=== Step 6: Updating host nginx ==="
sudo cp nginx-scanner.conf /etc/nginx/sites-available/scanner
sudo ln -sf /etc/nginx/sites-available/scanner /etc/nginx/sites-enabled/scanner
sudo rm -f /etc/nginx/sites-enabled/default

echo "=== Step 7: Testing nginx config ==="
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "=== Step 8: Restarting nginx ==="
    sudo systemctl restart nginx
    echo "=== DONE ==="
    echo ""
    echo "Test the website now: https://scanner.keerthiyakkala.com"
    echo ""
    echo "If still having issues, check:"
    echo "1. Browser console for specific errors"
    echo "2. docker logs vulnscan-frontend"
    echo "3. docker logs vulnscan-backend"
    echo "4. sudo tail -50 /var/log/nginx/scanner.error.log"
else
    echo "=== ERROR: Nginx config invalid ==="
    exit 1
fi
```

## Additional Backend CORS Fix

The backend [main.py](backend/main.py:32-44) has CORS configured but might need wildcard for production.

**Option A: Add wildcard (less secure, easier)**
Change line 32 in backend/main.py:
```python
allow_origins=["*"],  # Allow all origins
```

**Option B: Add your IP and all domain variations**
Keep the list but ensure it includes:
- `https://scanner.keerthiyakkala.com` ✓ (already there)
- `http://scanner.keerthiyakkala.com` ✓ (already there)
- Your AWS IP if accessing by IP

## Quick Diagnostic Commands

Run these on your server to see what's happening:

```bash
# 1. Check if frontend container has the files
docker exec vulnscan-frontend ls -la /usr/share/nginx/html/
docker exec vulnscan-frontend ls -la /usr/share/nginx/html/assets/

# 2. Check nginx config in container
docker exec vulnscan-frontend cat /etc/nginx/conf.d/default.conf

# 3. Test asset loading from within container
docker exec vulnscan-frontend curl -I http://localhost/assets/index-*.js

# 4. Test from host
curl -I http://127.0.0.1:3001/assets/index-*.js

# 5. Check logs
docker logs vulnscan-frontend --tail 50
docker logs vulnscan-backend --tail 50
sudo tail -50 /var/log/nginx/scanner.error.log
```

## What to Look For

### In Browser DevTools (F12 → Network tab):

**If you see 404 for assets:**
- Status Code: 404
- Request URL: `https://scanner.keerthiyakkala.com/assets/index-XXXXX.js`
- Response: 404 Not Found

**Cause:** Frontend container still has old nginx.conf OR host nginx is blocking

**Fix:** Rebuild frontend container (see script above)

### If you see CORS errors:

**Error:**
```
Access to fetch at 'http://127.0.0.1:8087/api/scan' from origin 'https://scanner.keerthiyakkala.com' has been blocked by CORS policy
```

**Cause:** Backend CORS doesn't allow your domain

**Fix:** Update backend CORS (see Option A or B above)

### If you see blank page but no errors:

**Symptoms:**
- No 404 errors
- No CORS errors
- Console is clean
- Page source shows `<div id="root"></div>` but it's empty

**Cause:** React not mounting - possible JS error being swallowed

**Fix:** Check:
1. View page source - should see script tags loading
2. Browser console → check for any warnings
3. Try hard refresh (Ctrl+Shift+R)

## Step-by-Step Manual Deployment

If the script doesn't work, do this manually:

```bash
# 1. Upload files
scp -r c:/work/vulnscan/* user@your-server:/opt/vulnscan/

# 2. SSH to server
ssh user@your-server
cd /opt/vulnscan

# 3. Stop everything
docker-compose down
sudo systemctl stop nginx

# 4. Rebuild containers
docker-compose build --no-cache

# 5. Start containers
docker-compose up -d

# 6. Wait
sleep 30

# 7. Verify containers
docker ps | grep vulnscan
docker logs vulnscan-frontend --tail 20
docker logs vulnscan-backend --tail 20

# 8. Test local access (IMPORTANT!)
curl -I http://127.0.0.1:3001/
ASSET=$(docker exec vulnscan-frontend ls /usr/share/nginx/html/assets/*.js | head -1 | xargs basename)
curl -I http://127.0.0.1:3001/assets/$ASSET

# ^ This MUST return 200 OK. If not, assets aren't being served.

# 9. Update host nginx
sudo cp nginx-scanner.conf /etc/nginx/sites-available/scanner
sudo ln -sf /etc/nginx/sites-available/scanner /etc/nginx/sites-enabled/scanner

# 10. Test nginx config
sudo nginx -t

# 11. Start nginx
sudo systemctl start nginx

# 12. Check status
sudo systemctl status nginx

# 13. Test website
curl -I https://scanner.keerthiyakkala.com
```

## If STILL Getting 404 After All This

The issue might be with how Vite builds the assets. Check:

```bash
# On your Windows machine
cd c:/work/vulnscan/frontend
npm run build

# Look at the output
ls -la dist/
ls -la dist/assets/

# You should see:
# dist/index.html
# dist/assets/index-XXXXX.js
# dist/assets/index-XXXXX.css
```

If assets aren't in `dist/assets/`, the build might be wrong.

Check `vite.config.js` - it should be using default output directory.

## Nuclear Option: Fresh Rebuild

If nothing works:

```bash
# On server
cd /opt/vulnscan
docker-compose down
docker system prune -af  # WARNING: Removes ALL unused Docker data
docker-compose build --no-cache
docker-compose up -d
```

This completely clears Docker cache and rebuilds everything from scratch.
