# Fix Blank Page Issue - Asset 404 Errors

## The Problem

**Symptoms:**
- Website loads but shows blank page
- index.html loads successfully (200 OK)
- `/assets/*.js` and `/assets/*.css` return 404
- Assets exist in container at `/usr/share/nginx/html/assets/`
- No server errors (502, 500, etc.)

**Root Cause:**
The nginx configuration had a location block for static assets that didn't specify the `root` directive. This caused nginx to fail serving the asset files even though they existed in the container.

**Fixed in:** [frontend/nginx.conf](frontend/nginx.conf) line 12

## The Fix

Added `root /usr/share/nginx/html;` to the static assets location block.

**Before:**
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, no-transform";
}
```

**After:**
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    root /usr/share/nginx/html;  # <-- ADDED THIS LINE
    expires 1y;
    add_header Cache-Control "public, no-transform";
}
```

## Deploy the Fix

### Option 1: Automated Script

```bash
# Upload files to server
scp -r c:/work/vulnscan/* user@your-server:/opt/vulnscan/

# SSH and run fix script
ssh user@your-server
cd /opt/vulnscan
chmod +x fix-blank-page.sh
./fix-blank-page.sh
```

### Option 2: Manual Commands

```bash
# On your server
cd /opt/vulnscan

# Rebuild frontend only (faster than full rebuild)
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Wait and test
sleep 10
curl -I http://127.0.0.1:3001/
curl -I http://127.0.0.1:3001/assets/index-*.js
```

### Option 3: Full Rebuild (use if other issues exist)

```bash
cd /opt/vulnscan
docker-compose down
docker-compose build --no-cache
docker-compose up -d
sleep 30
```

## Verify the Fix

### 1. Check container logs
```bash
docker logs vulnscan-frontend
```

Should show nginx starting successfully, no errors.

### 2. List files in container
```bash
docker exec vulnscan-frontend ls -la /usr/share/nginx/html/
docker exec vulnscan-frontend ls -la /usr/share/nginx/html/assets/
```

Should show:
- `index.html` in `/usr/share/nginx/html/`
- `index-XXXXX.js` and `index-XXXXX.css` in `/usr/share/nginx/html/assets/`

### 3. Test asset loading
```bash
# Get actual asset filename
ASSET=$(docker exec vulnscan-frontend ls /usr/share/nginx/html/assets/*.js | head -1 | xargs basename)

# Test if it returns 200 OK (not 404)
curl -I http://127.0.0.1:3001/assets/$ASSET
```

Should return `HTTP/1.1 200 OK`, not `404 Not Found`.

### 4. Check in browser
Open DevTools (F12) → Network tab → Refresh page

All assets should show `200` status:
- ✅ `index.html` - 200 OK
- ✅ `/assets/index-*.js` - 200 OK
- ✅ `/assets/index-*.css` - 200 OK

## Why This Happened

In nginx, location blocks inherit the `root` directive from the server block **only if they don't have their own**. The regex location block `~* \.(js|css...)$` was intercepting requests for static files but not properly serving them because:

1. It matched `/assets/index-XXXX.js`
2. It set cache headers
3. But it didn't have a `root` directive
4. Nginx couldn't determine where to serve the file from
5. Result: 404

By explicitly adding `root /usr/share/nginx/html;` to that location block, we ensure assets are served correctly.

## Alternative Solution (Simpler Config)

If you prefer a simpler nginx config, you can remove the separate static assets block entirely:

```nginx
server {
    listen 80;

    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;

        # Add caching directly here for all static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, no-transform";
        }
    }

    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /usr/share/nginx/html;
    }
}
```

But the current fix is correct and will work fine.

## Still Blank?

If the page is still blank after the fix:

### Check browser console for errors
Press F12 → Console tab. Look for:
- ❌ CORS errors → Check API config
- ❌ JavaScript errors → Check build output
- ❌ Failed API calls → Check backend is running

### Verify Vite build output
```bash
# On your local Windows machine
cd c:/work/vulnscan/frontend
npm run build

# Check that dist/assets/ contains JS and CSS files
ls dist/assets/
```

Should show files like:
- `index-XXXXX.js`
- `index-XXXXX.css`

### Check if it's a React Router issue
If assets load (200 OK) but page is still blank, it might be a React issue:

```bash
# Check browser console for React errors
# Check if React is rendering anything
# View page source - should see <div id="root"></div>
```

### Check host nginx (reverse proxy)
If using nginx as a reverse proxy on the host:

```bash
# Make sure reverse proxy isn't breaking asset paths
sudo tail -50 /var/log/nginx/scanner.error.log
sudo tail -50 /var/log/nginx/scanner.access.log | grep assets
```

The reverse proxy should pass through asset requests unchanged:
```nginx
location / {
    proxy_pass http://127.0.0.1:3001;
    # Should NOT modify asset paths
}
```
