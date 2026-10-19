#!/bin/bash
BACKUP_DIR="/var/local/path/backups"
DATE=$(date +%d_%b_%Y)
pg_dump -U postgres -h localhost db_name > "$BACKUP_DIR/${DATE}.sql"