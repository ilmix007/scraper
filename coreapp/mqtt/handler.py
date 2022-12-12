from typing import List

from django.conf import settings
from json.decoder import JSONDecodeError
import json
import uuid
import random
import paho.mqtt.client as mqtt
from coreapp.service.offers import OfferFace

import logging

LOGGER = logging.getLogger(__name__)


class MqttHandler:

    def __init__(self, server=settings.MQTT_SERVER, port=settings.MQTT_PORT):
        self.server = server
        self.port = port
        client_id = f'scraper-{random.randint(1, 1000)}'
        self.client = mqtt.Client(client_id=client_id, clean_session=True)
        self.client.username_pw_set(str(settings.MQTT_USERNAME), str(settings.MQTT_PASSWORD))

    def connect(self, topic=f'{settings.MQTT_TOPIC_REQUEST}/#'):
        status = self.client.connect(self.server, self.port)
        if status == 0:
            self.client.subscribe(topic)
            self.client.on_message = self.on_message
            self.client.loop_start()
            return True
        raise MqttException('MQTT: no connection')

    def on_message(self, client, userdata, msg):
        """
            Получает сообщения от mqtt.

            {"uuid": "c57af2c6-0dd3-4696-89b6-9c5292fe8fdf",
            "data": {"region_id": 47,
            "product_name": "Опора шаровая верхнего рычага передней подвески",
            "article": "4010A137", "brand": "BULLID"}, "app": "core"}
        """
        if msg.topic.find(settings.MQTT_TOPIC_REQUEST) >= 0:
            topic_uuid = msg.topic.split('/')[-1]
            try:
                core_session = str(uuid.UUID(topic_uuid, version=4))
            except (ValueError, TypeError):
                LOGGER.warning('Bad session UUID in mqtt topic')
                return
            try:
                data = str(msg.payload.decode())
                py_data = json.loads(data)
            except JSONDecodeError as jerr:
                LOGGER.error(f'Bad mqtt json, exception: {jerr}')
                return
            except Exception as ex:
                LOGGER.exception(f'Bad mqtt message, exception: {ex}')
                return
            session = py_data.get('uuid')
            article = py_data.get('data').get('article')
            brand = py_data.get('data').get('brand')
            if article and session:
                if brand:
                    offers = OfferFace.get_offer_by_art(article, brand)
                else:
                    offers = OfferFace.get_offer_by_art(article)
                self.send_answer(core_session, offers)

    def send_answer(self, core_session: str, offers: List):
        answer = {"app_name": "scraper",
                  "core_session": core_session,
                  "data": offers}
        LOGGER.debug(answer)
        session = uuid.uuid4()
        return self.client.publish(
            f"{settings.MQTT_TOPIC_RESPONSE}/{str(session)}",
            json.dumps(answer, ensure_ascii=False))


class MqttException(Exception):
    pass
