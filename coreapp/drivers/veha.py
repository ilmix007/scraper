from bs4 import BeautifulSoup
import re
from coreapp.drivers.base import BaseDriver, Link

import logging

LOGGER = logging.getLogger(__name__)


class Veha(BaseDriver):

    def parse_link_type(self, soup: BeautifulSoup, link: Link) -> Link:
        """Определяет тип ссылки"""
        if len(re.findall(r'/catalog/product/\d*', link.url)) > 0:
            link.type_link.product = True
        return link
