from typing import List
from urllib.parse import urljoin, urlparse

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
            link.offer = False
            link.img = False
            link.shop = False
            return link
        if len(re.findall(r'/catalog/product/\d*', link.url)) > 0:
            link.offer = True
            link.shop = True
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

    def _get_count(self, soup: BeautifulSoup) -> int:
        availabilitys = soup.findAll('div', class_="product-card__stock-count")
        for av in availabilitys:
            if 'в наличии' in av.text.lower():
                count = soup.findAll('span', class_='red-text')[0].text
                count = count.replace('\n', '').replace(' ', '')
                count = re.findall(r'\d+', count)
                if len(count) == 1:
                    return int(count[0])
                break
        else:
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
                for content in tr.contents:
                    if 'Артикул' in content.text:
                        arr = [value for value in tr.contents if value != ' ']
                        article = arr[1].text
                    elif 'Производитель' in content.text:
                        arr = [value for value in tr.contents if value != ' ']
                        brand = arr[1].text
                    else:
                        arr = [value for value in tr.contents if value != ' ']
                        parameters.append(ParameterData(content.text, arr[1].text))
        return name, article, brand

    def get_offers(self, soup: BeautifulSoup, shop_id: int, link_data: LinkData) -> List[OfferData]:
        """Возвращает офферы"""
        name, article, brand = self._get_product(soup)
        price = self._get_price(soup)
        count = self._get_count(soup)
        if count == 0:
            return []
        offer = OfferData(name=name, brand=brand, article=article, images=[], parameters=[],
                          count=count, price=price, shop_id=shop_id, link=link_data)
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
        for addr_tag in addresses:
            address = addr_tag.text.replace('\n', '')
            shop_link = addr_tag.a.attrs.get('href')
            shop_link.replace('/shop_change/', '').replace('/', '')
            ids = re.findall(r'\d+', shop_link)
            tabid = addr_tag.parent.parent.attrs.get('data-tabid')
            if len(ids) == 1:
                city = city_dict[tabid]
                name = f'{city} - {address}'
                shop = ShopData(name=name, city=city, address=address, shop_param=f'?change_city={ids[0]}')
                result.append(shop)
        return result

    def get_links(self, soup: BeautifulSoup, link: LinkData) -> List[LinkData]:
        """Возвращает список ссылок"""
        prod_links = soup.findAll('a', class_='product__pic product__pic--item')
        url_obj = urlparse(link.url)
        host = urlparse(link.url).netloc
        result = list()
        for pl in prod_links:
            alt = pl.img.attrs.get('alt')
            url = pl.attrs.get('href')
            url = urljoin(f'{url_obj.scheme}://{url_obj.netloc}', url)
            link = LinkData(url=url, alt=alt, offer=True, shop=False, img=False)
            result.append(link)
        return result
