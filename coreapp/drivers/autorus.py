from typing import List

from bs4 import BeautifulSoup

from coreapp.drivers.base import BaseDriver, OfferData, LinkData, ShopData

import logging

LOGGER = logging.getLogger(__name__)


class Autorus(BaseDriver):
    def get_offers(self, soup: BeautifulSoup, shop_id: int, link_data: LinkData) -> List[OfferData]:
        """Получить список оферов"""
        pass

    def get_link_type(self, soup: BeautifulSoup, link: LinkData) -> LinkData:
        """Определить тип ссылки"""
        pass

    def get_links(self, soup: BeautifulSoup, link: LinkData) -> List[LinkData]:
        """Возвращает список ссылок"""
        pass

    def get_shops(self, soup: BeautifulSoup, link: LinkData) -> List[ShopData]:
        """Получить список магазинов"""
        pass

