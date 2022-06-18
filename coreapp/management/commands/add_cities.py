# pylint: disable=E1101
from django.core.management.base import BaseCommand
import json
from pathlib import Path
import os
import psycopg2
import logging

from coreapp.management.commands.areas import AREAS
from coreapp.models import Region, City

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create regions and cities"

    def handle(self, *args, **kwargs):
        City.objects.all().delete()
        Region.objects.all().delete()
        russia = AREAS[0]
        for region_dict in russia['areas']:
            region_obj, _ = Region.objects.get_or_create(name=region_dict["name"],
                                                         defaults={"name": region_dict["name"]}, )
            for city in region_dict['areas']:
                if '(' in city["name"]:
                    city_arr = city["name"].split(' (')
                    city_name = city_arr[0]
                    description = city_arr[-1].split(')')[0]
                else:
                    city_name = city["name"]
                    description = None
                city_obj, _ = City.objects.get_or_create(name=city_name, region=region_obj, description=description,
                                                         defaults={"name": city_name, "region": region_obj,
                                                                   'description': description})
        LOGGER.info(f"Regions: {Region.objects.all().count()}")
        LOGGER.info(f"Cities: {City.objects.all().count()}")
