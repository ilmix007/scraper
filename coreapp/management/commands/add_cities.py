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
        russia = AREAS[0]
        for region_dict in russia['areas']:
            region_obj, _ = Region.objects.get_or_create(name=region_dict["name"],
                                                         defaults={"name": region_dict["name"]}, )
            for city in region_dict['areas']:
                city_name = city["name"].split(' (')[0] if '(' in city["name"] else city["name"]
                city_obj, _ = City.objects.get_or_create(name=city_name, region=region_obj,
                                                         defaults={"name": city["name"], "region": region_obj})
            regions = Region.objects.all().count()
            cities = City.objects.all().count()
            LOGGER.info(f"Регионы: {regions}")
            LOGGER.info(f"Города: {cities}")
