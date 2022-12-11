import json
import time
import uuid

from django.conf import settings
import paho.mqtt.client as mqtt
from uuid import UUID
import random
import logging

from coreapp.service.finder import ProuctFace

LOGGER = logging.getLogger(__name__)


class Handler:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def run(self):
        """
            Цикл проверяющий и отдающий подсказки и предложения
            из zzap на mqtt
        """
        while True:
            time.sleep(1)
            if len(self.mqtt_client.offer_order) > 0:
                try:
                    key, item = self.mqtt_client.offer_order.popitem()
                except Exception as ex:
                    LOGGER.debug(f'mqtt_handler.offer_order.popitem: {ex}')
                    continue
                # data, session = self.search_offer(item)
                # if isinstance(data, dict):
                #     self.send_answer(data, session)
                #     continue
            if len(self.mqtt_client.suggests_order) > 0:
                try:
                    session, resp = self.mqtt_client.suggests_order.popitem()
                except Exception as ex:
                    LOGGER.debug(f'mqtt_handler.suggests_order.popitem: {ex}')
                    continue
                prods = ProuctFace.get_products(resp.text)
                print("prods")
                print(prods)
                if isinstance(prods, list):
                    self.send_answer(prods, session, datatype='product')
                    continue

    def send_answer(self, data: list, session: uuid.UUID, datatype):
        """Отправка данных в mqtt"""

        if datatype == "product":
            return self.mqtt_client.client.publish(
                f"{settings.MQTT_TOPIC_RESPONSE}/suggests/{session}",
                json.dumps(data, ensure_ascii=False))
        return False

