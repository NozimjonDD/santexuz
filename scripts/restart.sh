#!/usr/bin/env bash

pip install -r requirements/production.txt

python manage.py collectstatic --noinput


python manage.py migrate

#sudo systemctl restart gunicorn.service
#sudo systemctl restart celery.service
#sudo systemctl restart celerybeat.service

echo -e "\033[1m Restarted! \033[0m"
