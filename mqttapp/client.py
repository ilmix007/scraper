import json

from django.conf import settings
import paho.mqtt.client as mqtt

from uuid import UUID
import random
import logging
from mqttapp.models import MqttResponse

LOGGER = logging.getLogger(__name__)


class Client:
    def __init__(self):
        self.t_out = 1
        self.server = settings.MQTT_SERVER
        self.port = settings.MQTT_PORT
        self.topic = f'{settings.MQTT_TOPIC_REQUEST}/#'
        self.client_id = f'zzap-{random.randint(1, 100)}'
        self.answer = ''
        self.client = mqtt.Client(client_id=self.client_id, clean_session=True)
        self.client.username_pw_set(
            str(settings.MQTT_USERNAME), str(settings.MQTT_PASSWORD))
        self.suggests_order = dict()
        self.offer_order = dict()

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
            except Exception as ex:
                LOGGER.exception(f'Bad mqtt message, exception: {ex}')
                return
            if msg.topic.find("geozip/request/suggests") >= 0:
                text = py_data.get('data').get('request')
                if text and session:
                    resp = MqttResponse(text=text, session=session, topic='product')
                    self.suggests_order.update({session: resp})
            elif msg.topic.find("geozip/request/offers") >= 0:
                data = py_data.get('data').get('request')
                if data and session:
                    self.offer_order.update({session: data})


class MqttException(Exception):
    pass
