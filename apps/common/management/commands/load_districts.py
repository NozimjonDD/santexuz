import json
from django.core.management.base import BaseCommand

from apps.common.management import utils


class Command(BaseCommand):
    help = "Load districts from json file"

    def handle(self, *args, **options):
        utils.update_districts()

        self.stdout.write(self.style.SUCCESS("Districts loaded successfully"))
