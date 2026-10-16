#!/usr/bin/env bash

# Create directories if they don't exist
mkdir -p storage/{logs,}
mkdir -p media/
mkdir -p static/
touch storage/logs/celery.log
touch storage/logs/security.log
touch storage/logs/app.log

# Set directory permissions
chmod -R 755 storage/
chmod 755 media/
chmod 755 static/

# Set file permissions
find storage/ -type f -exec chmod 644 {} \;
find storage/logs -type f -exec chmod 644 {} \;
find storage/logs -type f -name "*.log" -exec chmod -R 777 {} \;
find media/ -type f -exec chmod 644 {} \;

# Set ownership (web server user)
chown -R www-data:www-data storage/
chown -R www-data:www-data media/
sudo apt-get install redis-server -y

echo "Permissions set successfully!"