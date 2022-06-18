from typing import List

from bs4 import BeautifulSoup
import re
from coreapp.drivers.base import BaseDriver, LinkData, OfferData, ParameterData, ShopData

import logging

LOGGER = logging.getLogger(__name__)


class Veha(BaseDriver):

    def get_link_type(self, soup: BeautifulSoup, link: LinkData) -> LinkData:
        """Определяет тип ссылки"""
        page_404 = soup.findAll('div', class_='page-404', limit=1)
        if len(page_404) > 0:
            link.product = False
            link.img = False
            link.shop = False
            return link
        if len(re.findall(r'/catalog/product/\d*', link.url)) > 0:
            link.product = True
        if '/kontakty/' in link.url:
            link.shop = True
        return link

    def _get_price(self, soup: BeautifulSoup) -> int:
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

    def _get_product(self, soup: BeautifulSoup) -> (str, str, str):
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
                        parameters.append(ParameterData(content.text, tr.contents[index + 1]))
        return name, article, brand

    def get_offers(self, soup: BeautifulSoup) -> List[OfferData]:
        """Возвращает офферы"""
        name, article, brand = self._get_product(soup)
        price = self._get_price(soup)
        offer = OfferData(name=name, brand=brand, article=article, images=[], parameters=[],
                          count=0, price=price)
        return [offer]

    def get_shops(self, soup: BeautifulSoup, link: LinkData) -> List[ShopData]:
        # https://veha-corp.ru/shop_change/9/
        # ?change_city=15
        cities = soup.findAll('div', class_='shops-cities-popup__city-btn')
        city_dict = dict()
        for city in cities:
            key = city.parent.attrs.get('data-tabid')
            value = city.text
            city_dict.update({key: value})

        addresses = soup.findAll('li', class_='shops-cities-popup__shop')
        result = list()
        for address in addresses:
            adr = address.text.replace('\n', '')
            shop_link = address.a.attrs.get('href')
            shop_link.replace('/shop_change/', '').replace('/', '')
            ids = re.findall(r'\d+', shop_link)
            tabid = address.parent.parent.attrs.get('data-tabid')
            if len(ids) == 1:
                city = city_dict[tabid]
                name = f'{city} - {adr}'
                shop = ShopData(name=name, city=city, address=address, shop_param=f'?change_city={ids[0]}')
                result.append(shop)
        return result

    def get_links(self, soup: BeautifulSoup, link: LinkData) -> List[LinkData]:
        """Возвращает список ссылок"""
        pass
