from django.core.management.base import BaseCommand

from mqttapp.client import Client
from mqttapp.handler import Handler

import logging

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Поиск товаров и предложений на zzap.ru"

    def handle(self, *args, **kwargs):
        mqtt_client = Client()
        mqtt_client.connect()
        handler = Handler(mqtt_client)
        handler.run()
