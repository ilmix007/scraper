import logging

from django.core.management.base import BaseCommand

from coreapp.drivers.conf import DRIVER_CONF
from coreapp.models import Site

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Add coordinate for meter'

    def handle(self, *args, **options):
        LOGGER.info('Start adding sites')
        for domain in DRIVER_CONF.keys():
            site, created = Site.objects.get_or_create(domain=domain, defaults={'domain': domain})
            if created:
                LOGGER.info(f'Created {site}')
            else:
                LOGGER.info(f'{site} exists')
        LOGGER.info('Finish adding sites')
