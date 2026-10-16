from __future__ import absolute_import
import os
from django.apps import apps
from celery import Celery
from django.conf import settings
from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE',  os.getenv("DJANGO_SETTINGS_MODULE"))

app = Celery('project_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.config_from_object(settings)
app.autodiscover_tasks()
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])


# Setup logging
@app.task(bind=True)
def debug_task(self):
    from celery.utils.log import get_task_logger
    logger = get_task_logger(__name__)
    logger.info('Task running...')
