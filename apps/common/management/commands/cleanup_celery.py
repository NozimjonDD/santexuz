# management/commands/cleanup_celery.py
# Put this in: course/management/commands/cleanup_celery.py

from django.core.management.base import BaseCommand
from ohayo_academy.celery import app
import redis


class Command(BaseCommand):
    help = 'Clean up all pending Celery tasks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--purge-only',
            action='store_true',
            help='Only purge tasks, don\'t clear Redis',
        )
        parser.add_argument(
            '--redis-only',
            action='store_true',
            help='Only clear Redis, don\'t purge tasks',
        )

    def handle(self, *args, **options):
        if options['redis_only']:
            self.clear_redis()
        elif options['purge_only']:
            self.purge_tasks()
        else:
            self.purge_tasks()
            self.clear_redis()

        self.stdout.write(
            self.style.SUCCESS('Successfully cleaned up Celery tasks!')
        )

    def purge_tasks(self):
        self.stdout.write('Purging all pending tasks...')
        app.control.purge()

    def clear_redis(self):
        self.stdout.write('Clearing Redis broker...')
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.flushdb()