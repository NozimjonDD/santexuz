import json

from apps.common import models


def update_regions():
    file_name = "apps/common/management/data/regions.json"
    with open(file_name, "r") as file:
        regions = json.load(file)

        for region in regions:
            models.Region.objects.update_or_create(
                soato=region["soato"],
                defaults={
                    "name_uz": region["name"],
                    "name_ru": region["name_ru"],
                    "name_en": region["name_en"],
                }
            )


def update_districts():
    file_name = "apps/common/management/data/districts.json"

    with open(file_name, "r", encoding='utf-8') as file:
        districts = json.load(file)

        for district in districts:
            models.District.objects.update_or_create(
                soato=district["soato"],
                defaults={
                    "name_uz": district["name"],
                    "name_ru": district["name_ru"],
                    "name_en": district["name_en"],
                    "region": models.Region.objects.get(soato=str(district["soato"])[:4]),
                }
            )
