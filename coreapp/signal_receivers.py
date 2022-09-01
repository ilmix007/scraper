from django.conf import settings
from django.dispatch import receiver
from django import dispatch
from typing import Union

import uuid
import json

from coreapp.models.products import Offer

import logging
LOGGER = logging.getLogger(__name__)


mqtt_offer_results_signal = dispatch.Signal()


@receiver(mqtt_offer_results_signal)
def mqtt_offer_results_receiver(sender, **kwargs):
    """
        Ресивер для предложений от скрапера.
    """
    if len(sender.offer_order) > 0:
        try:
            key, item = sender.offer_order.popitem()
        except Exception as ex:
            LOGGER.debug(f'mqtt.offer_order.popitem: {ex}')
        data, session = search_offer(sender, item)
        if isinstance(data, dict):
            send_answer(sender, data, session)


def search_offer(sender, request_data: Union[tuple, dict]):
    """g
        Получаем массив с результатами поиска от скрапера.
    """
    # accept_uuid, zzap_req = request_data
    # partnumber = zzap_req.get('article')
    partnumber = request_data.get('article')
    offers_list = []
    one_offer = {}
    offers = Offer.objects.filter(product__article__art=partnumber)
    for offer in offers:
        one_offer['shop_name'] = offer.shop.name
        one_offer['price'] = offer.price
        one_offer['quantity'] = offer.count
        one_offer['link'] = offer.link.url
        one_offer['domain'] = offer.link.site.domain
        one_offer['address'] = f'{offer.shop.city}, {offer.shop.address}'
        offers_list.append(one_offer)
        one_offer = {}

    uuid_req = uuid.uuid4()
    session = uuid.uuid4()
    data = {
        # "accept_uuid": str(accept_uuid),
        "uuid": str(uuid_req),
        "data": offers_list,
        "app": "scraper",
        "type": "offer"
    }
    return data, str(session)


def send_answer(sender, data: dict, session: uuid.UUID):
    """Отправка данных в mqtt"""
    if data.get("type") == "offer":
        return sender.client.publish(
            f"{settings.MQTT_TOPIC_RESPONSE}/scraper/{session}",
            json.dumps(data, ensure_ascii=False))
    return False
