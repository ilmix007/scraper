import requests
from bs4 import BeautifulSoup
import logging

LOGGER = logging.getLogger(__name__)
__all__ = ['BaseDriver']


class Shop:
    """Магазин"""

    def __init__(self, url, phone, name='', address='', city=''):
        self.name = name
        self.address = address
        self.phone = phone
        self.url = url
        self.city = city


class Product:
    """Товар"""

    def __init__(self, name, brand='', article=''):
        self.name = name
        self.brand = brand
        self.article = article


class Offer:
    """Товарное предложение"""

    def __init__(self, product, shop, url, count=0):
        self.product = product
        self.count = count
        self.shop = shop
        self.url = url


class BaseDriver:
    """Фасад для работы с сайтом"""

    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/50.0.2661.102 Safari/537.36'
        # 'Mozilla/5.0(X11; Linux x86_64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 102.0.5005.61 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}
        self.soup = None

    def get_robots(self, url):
        result_data_set = dict()
        result = requests.get(url, headers=self.headers)
        if result.status_code == 200:
            result = result.content.decode()
            result = result.replace('\r', '')
            for line in result.split("\n"):
                result = result.replace('\r', '')
                key = line.split(': ')[0].split(' ')[0]
                value = line.split(': ')[1].split(' ')[0]
                if key not in result_data_set.keys():
                    result_data_set[key] = list()
                result_data_set[key].append(value)
            return result_data_set, True
        else:
            LOGGER.error(f"Error receiving robots.txt {result}")
            return dict(), False

    def _process_sitemap(self, soup):
        """Рекурсивная функция обработки sitemap"""
        result_urls = list()
        sitemap_tags = soup.find_all("sitemap")
        for sitemap in sitemap_tags:
            url = sitemap.findNext("loc").text
            result = requests.get(url, headers=self.headers)
            if result.status_code == 200:
                soup = BeautifulSoup(result.content, features='xml')
                result_urls.extend(self._process_sitemap(soup))
            else:
                LOGGER.error(f"Error receiving sitemap {result}")
            break
        result_urls.extend(soup.find_all("url"))
        return result_urls

    def get_urls_from_sitemap(self, sitemap_urls):
        for url in sitemap_urls:
            result = requests.get(url, headers=self.headers)
            if result.status_code == 200:
                soup = BeautifulSoup(result.content, features='xml')
                return self._process_sitemap(soup)
            else:
                LOGGER.error(f"Error receiving sitemap {result}")
                return False

    def scrape(self, url) -> list[Offer]:
        """Возвращает список офферов"""
        pass

    def get_shops(self, url) -> list[Shop]:
        """Возвращает список магазинов"""
        pass
