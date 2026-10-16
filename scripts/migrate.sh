#!/usr/bin/env bash
set -e

#echo "Creating database backup..." # todo
#pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

echo "Running migrations..."
python manage.py migrate --check
python manage.py migrate

echo "Running data migrations..."
python manage.py run_data_migrations

echo "Verifying deployment..."
python manage.py check --deploy