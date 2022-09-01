from django.conf import settings
from json.decoder import JSONDecodeError
import json
from uuid import UUID
import random
import paho.mqtt.client as mqtt

from coreapp.signal_receivers import mqtt_offer_results_signal

import logging
LOGGER = logging.getLogger(__name__)


class MqttHandler:
    server = settings.MQTT_SERVER
    port = settings.MQTT_PORT
    topic = f'{settings.MQTT_TOPIC_REQUEST}/#'
    client_id = f'zzap-{random.randint(1, 100)}'
    client = mqtt.Client(client_id=client_id, clean_session=True)
    client.username_pw_set(
        str(settings.MQTT_USERNAME), str(settings.MQTT_PASSWORD))
    suggests_order = dict()
    offer_order = dict()
    offers_results = dict()
    request_accept_queue = list()
    response_accept_queue = list()

    def connect(self):
        status = self.client.connect(self.server, self.port)
        if status == 0:
            self.client.subscribe(self.topic)
            self.client.on_message = self.on_message
            self.client.loop_start()
            return True
        raise MqttException('MQTT: no connection')

    def on_message(self, client, userdata, msg):
        """
            Получает сообщения от mqtt.
        """
        if msg.topic.find("geozip/request") >= 0:
            topic_uuid = msg.topic.split('/')[-1]
            try:
                session = UUID(topic_uuid, version=4)
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
            if msg.topic.find("geozip/request/scraper") >= 0:
                text = py_data.get('data').get('request')
                # accept_uuid = py_data.get('accept_uuid')

                # if text and session and accept_uuid:
                if text and session:
                    # self.offer_order.update({session: (accept_uuid, text)})
                    self.offer_order.update({session: text})
                    mqtt_offer_results_signal.send(sender=self.__class__)


class MqttException(Exception):
    pass
