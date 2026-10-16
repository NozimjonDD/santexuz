# Create a Backup Script
- sudo nano /backup_script.sh  
- sudo chmod +x /backup_script.sh
- sudo nano /root/.pgpass
- localhost:5432:gossip_db1:postgres:your_password
- sudo chmod 600 /root/.pgpass

# Test the Script
- sudo `/backup_script.sh`

# Schedule the Backup with Cron
- sudo crontab -e
- 0 2 * * * /backup_script.sh  
- # backup ([ 0 2 * * * ] e.g., daily at 2 AM)

# Optional: Handle sudo Without Password
- sudo visudo
- ubuntu ALL=(ALL) NOPASSWD: /usr/bin/pg_dump

# Verify the Cron Job
- sudo grep CRON /var/log/syslog