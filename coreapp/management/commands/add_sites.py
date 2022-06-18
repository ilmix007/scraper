import logging

from django.core.management.base import BaseCommand

from coreapp.drivers.conf import DRIVER_CONF
from coreapp.models import Site

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Add coordinate for meter'

    def handle(self, *args, **options):
        LOGGER.info('Start add coordinate for meters')
        for domen in DRIVER_CONF.keys():
            site, created = Site.objects.get_or_create(url=domen, defaults={'url': domen})
            if created:
                LOGGER.info(f'Created {site}')
            else:
                LOGGER.info(f'{site} exists')


        LOGGER.info('Finish add coordinate for meters')
