import json
from django.core.management.base import BaseCommand

from apps.common.management import utils


class Command(BaseCommand):
    help = "Load regions from json file"

    def handle(self, *args, **options):
        utils.update_regions()

        self.stdout.write(self.style.SUCCESS("Regions loaded successfully"))
