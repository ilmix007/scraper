from random import randint
import requests
from bs4 import BeautifulSoup
import logging
from coreapp.drivers.user_agents import USER_AGENTS
from django.conf import settings

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
    """Базовый класс драйверов"""

    def __init__(self):
        self.user_agent = USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
        self.headers = {'User-Agent': self.user_agent}
        self.soup = None

    def process_robots(self, robots_txt: str) -> dict:
        result_data_set = dict()
        robots_txt = robots_txt.replace('\r', '')
        robots_txt = robots_txt.replace('\t', '')
        robots_arr = robots_txt.split()
        if len(robots_arr) > 0:
            if len(robots_arr[0]) > 30 and len(robots_arr) < 2:
                for item in settings.ROBOT_KEYS:
                    robots_txt = robots_txt.replace(f' {item}', f'\n{item}')
        for line in robots_txt.split("\n"):
            if len(line) > 0:
                if line[0] != '#':
                    robots_txt = robots_txt.replace('\r', '')
                    key = line.split(': ')[0].split(' ')[0]
                    value = line.split(': ')[1].split(' ')[0]
                    if key not in result_data_set.keys():
                        result_data_set[key] = list()
                    result_data_set[key].append(value)
        return result_data_set

    def get_robots(self, url: str):
        try:
            result = requests.get(url, headers=self.headers)
        except Exception as ex:
            LOGGER.warning(f"Error 1 attempt receiving robots.txt. Exception: {ex}")
            result = requests.get(url, headers=self.headers, verify=False)
            if result.status_code == 200:
                result_data_set = self.process_robots(result.content.decode())
                return result_data_set, True
        else:
            if result.status_code == 200:
                result_data_set = self.process_robots(result.content.decode())
                return result_data_set, True
        LOGGER.error(f"Error receiving robots.txt\n Url: {url}, \nresult: {result}. User-agent: {self.user_agent}")
        return dict(), False

    def _process_sitemap(self, soup: BeautifulSoup) -> list:
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
                LOGGER.error(f"Error receiving sitemap {result}. User-agent: {self.user_agent}")
        result_urls.extend(soup.find_all("url"))
        return result_urls

    def get_urls_from_sitemap(self, sitemap_urls):
        """Возвращает ссылки с sitemap"""
        for url in sitemap_urls:
            result = requests.get(url, headers=self.headers)
            if result.status_code == 200:
                soup = BeautifulSoup(result.content, features='xml')
                return self._process_sitemap(soup)
            else:
                LOGGER.error(f"Error receiving sitemap {result}. User-agent: {self.user_agent}")
                return False

    def scrape(self, url) -> list[Offer]:
        """Возвращает список офферов"""
        return list()

    def get_shops(self, url) -> list[Shop]:
        """Возвращает список магазинов"""
        return list()
