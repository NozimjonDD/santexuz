sudo apt install supervisor
sudo systemctl start supervisor
sudo systemctl enable supervisor

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery
sudo supervisorctl start celerybeat

# Run commands
celery - A project_backend worker -l info
celery_beat - celery -A project_backend beat -l info
# or
celery_beat - celery -A project_backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler