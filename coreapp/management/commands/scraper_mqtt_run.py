from django.core.management.base import BaseCommand
import time

from coreapp.mqtt.mqtt import MqttHandler

import logging
LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Поиск товаров и предложений от скрапера"

    def handle(self, *args, **kwargs):
        mqtt_handler = MqttHandler()
        mqtt_handler.connect()
        while True:
            time.sleep(300)
