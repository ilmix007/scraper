from bs4 import BeautifulSoup

from coreapp.drivers.base import BaseDriver, Link

import logging

LOGGER = logging.getLogger(__name__)


class Veha(BaseDriver):

    def parse_link_type(self, soup: BeautifulSoup, link: Link) -> Link:
        """Обновляет тип ссылки"""
        return link
