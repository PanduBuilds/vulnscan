================================================================================
QUICK FIX FOR 502 ERROR - scanner.keerthiyakkala.com
================================================================================

STEP 1: Upload files to your server
------------------------------------
From Windows, run in PowerShell or Git Bash:

    scp -r c:/work/vulnscan/* user@your-server:/opt/vulnscan/

Replace 'user@your-server' with your actual server login.


STEP 2: SSH to server and run the fix script
---------------------------------------------
    ssh user@your-server
    cd /opt/vulnscan
    chmod +x fix-502.sh
    sudo ./fix-502.sh


That's it! The script will:
  ✓ Rebuild all Docker containers
  ✓ Wait for them to start properly
  ✓ Configure nginx correctly
  ✓ Test the website

================================================================================
ALTERNATIVE: Manual Commands (if script doesn't work)
================================================================================

SSH to your server, then copy-paste this entire block:

cd /opt/vulnscan && \
docker-compose down && \
docker-compose build --no-cache && \
docker-compose up -d && \
echo "Waiting 30 seconds..." && sleep 30 && \
sudo cp nginx-scanner.conf /etc/nginx/sites-available/scanner && \
sudo ln -sf /etc/nginx/sites-available/scanner /etc/nginx/sites-enabled/scanner && \
sudo rm -f /etc/nginx/sites-enabled/default && \
sudo nginx -t && \
sudo systemctl restart nginx && \
echo "Done! Check https://scanner.keerthiyakkala.com"

================================================================================
TROUBLESHOOTING
================================================================================

If you still get 502 error:

1. Check if containers are running:
   docker ps | grep vulnscan

2. Test local access:
   curl -I http://127.0.0.1:3001
   curl http://127.0.0.1:8087/

3. Check nginx logs:
   sudo tail -50 /var/log/nginx/scanner.error.log

4. Check Docker logs:
   docker logs vulnscan-frontend
   docker logs vulnscan-backend

5. If on CentOS/RHEL and see "Permission denied":
   sudo setsebool -P httpd_can_network_connect 1
   sudo systemctl restart nginx

================================================================================
For detailed troubleshooting, see:
  - FINAL-FIX.md
  - TROUBLESHOOTING-502.md
  - DEPLOY-NOW.md
================================================================================
