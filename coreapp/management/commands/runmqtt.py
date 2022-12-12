import time
from coreapp.mqtt.handler import MqttHandler
import logging
from django.core.management.base import BaseCommand

LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Обрабатывает запросы с ядра по mqtt'

    def handle(self, *args, **options):
        LOGGER.info('Start MqttHandler')
        mqtt_handler = MqttHandler()
        mqtt_handler.connect()
        while True:
            time.sleep(3600)
