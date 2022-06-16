from typing import List

from bs4 import BeautifulSoup
import re
from coreapp.drivers.base import BaseDriver, Link, Offer, Product, Parameter

import logging

LOGGER = logging.getLogger(__name__)


class Veha(BaseDriver):

    def parse_link_type(self, soup: BeautifulSoup, link: Link) -> Link:
        """Определяет тип ссылки"""
        page_404 = soup.findAll('div', class_='page-404', limit=1)
        if len(page_404) > 0:
            link.type_link.product = False
            link.type_link.img = False
            link.type_link.shop = False
            return link
        if len(re.findall(r'/catalog/product/\d*', link.url)) > 0:
            link.type_link.product = True
        return link


def get_price(self, soup: BeautifulSoup) -> int:
    price = soup.findAll('div', class_='product-card__price')[0].text
    price = price.replace('\n', '').replace(' ', '')
    prices = re.findall(r'\d+\.\d+', price)
    if len(prices) == 1:
        return int(float(prices[0]))
    else:
        prices = re.findall(r'\d+', price)
        if len(prices) == 1:
            return int(prices[0])
        return 0


def get_product(self, soup):
    h1 = soup.findAll('h1', class_="title-lg", limit=1)
    name = h1[0].contents[0]
    parameters = list()
    tables = soup.findAll('table', class_="product-card__properties")
    brand = ''
    article = ''
    for table in tables:
        trs = table.findAll('tr')
        for tr in trs:
            for index, content in enumerate(tr.contents):
                if content.text == 'Артикул':
                    article = tr.contents[index + 1]
                elif content.text == 'Производитель':
                    brand = tr.contents[index + 1]
                elif index + 1 < len(tr.contents):
                    parameters.append(Parameter(content.text, tr.contents[index + 1]))
    product = Product(name, brand, article, parameters)
    return product


def parse_offers(self, soup: BeautifulSoup, link: Link) -> List[Offer]:
    """Возвращает список оферов"""
    product = self.get_product(soup)
    price = self.get_price(soup)
    # offer = Offer(product=product, price=0, count=0)
    return list()
