# Deployment Instructions for scanner.keerthiyakkala.com

## Prerequisites
- A server with Docker and Docker Compose installed
- Nginx installed on the host system
- Domain `scanner.keerthiyakkala.com` pointing to your server's IP address
- SSL certificate (can be obtained via Let's Encrypt)

## Step 1: Deploy Docker Containers

1. Copy the project files to your server:
```bash
rsync -avz --exclude node_modules --exclude .git . user@your-server:/opt/vulnscan/
```

2. SSH into your server:
```bash
ssh user@your-server
cd /opt/vulnscan
```

3. Start the Docker containers:
```bash
docker-compose up -d --build
```

4. Verify containers are running:
```bash
docker ps
```
You should see:
- `vulnscan-frontend` on port 3001
- `vulnscan-backend` on port 8087
- `vulnscan-dvwa` on port 8086

## Step 2: Configure Nginx Reverse Proxy

1. Copy the nginx configuration file:
```bash
sudo cp nginx-scanner.conf /etc/nginx/sites-available/scanner
```

2. Create a symbolic link to enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/scanner /etc/nginx/sites-enabled/scanner
```

3. Test nginx configuration:
```bash
sudo nginx -t
```

## Step 3: Set Up SSL Certificate (if not already done)

1. Install Certbot (if not installed):
```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

2. Obtain SSL certificate:
```bash
sudo certbot --nginx -d scanner.keerthiyakkala.com
```

Certbot will automatically configure SSL in your nginx config.

## Step 4: Restart Nginx

```bash
sudo systemctl restart nginx
```

## Step 5: Verify Deployment

1. Check that nginx is running:
```bash
sudo systemctl status nginx
```

2. Test the website:
```bash
curl -I https://scanner.keerthiyakkala.com
```

3. Open your browser and navigate to: https://scanner.keerthiyakkala.com

## Troubleshooting

### Check Docker containers
```bash
docker-compose logs -f
```

### Check Nginx logs
```bash
sudo tail -f /var/log/nginx/scanner.error.log
sudo tail -f /var/log/nginx/scanner.access.log
```

### Check if ports are accessible
```bash
curl http://localhost:3001
curl http://localhost:8087/
```

### Restart everything
```bash
docker-compose restart
sudo systemctl restart nginx
```

## Updating the Application

To update after making changes:

```bash
git pull  # or rsync files again
docker-compose down
docker-compose up -d --build
```

## Security Notes

- The DVWA container (vulnscan-dvwa) is intentionally vulnerable and should NOT be exposed to the public internet
- It's bound to 127.0.0.1:8086 by default for testing purposes only
- Consider adding firewall rules to restrict access
- Keep your SSL certificates up to date (Certbot auto-renewal should handle this)
