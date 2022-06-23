import time
from abc import ABC, abstractmethod
from random import randint
from typing import List, Dict, Any, Set
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import logging
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from coreapp.drivers.user_agents import USER_AGENTS
from django.conf import settings
from dataclasses import dataclass, field

LOGGER = logging.getLogger(__name__)
__all__ = ['BaseDriver', 'Driver', 'LinkData', 'ShopData', 'ParameterData', 'OfferData']


@dataclass
class LinkData:
    """Параметры ссылки"""
    url: str
    alt: str = ''
    offer: bool = False
    shop: bool = False
    img: bool = False


@dataclass
class ShopData:
    """Магазин"""
    name: str
    city: str
    address: str = ''
    phone: str = ''
    url: str = ''
    shop_param: str = ''

    def __str__(self):
        return self.name


@dataclass
class ParameterData:
    """Параметры товара"""
    name: str
    value: str


@dataclass
class OfferData:
    """Товарное предложение"""
    shop_id: int
    link: LinkData
    images: List
    parameters: List
    count: int = 0
    name: str = ''
    brand: str = ''
    article: str = ''
    price: float = 0


class BaseDriver(ABC):
    """Базовый класс драйвера"""

    def __init__(self):
        self.user_agent = USER_AGENTS[randint(0, len(USER_AGENTS) - 1)]
        self.headers = {'User-Agent': self.user_agent}

    @abstractmethod
    def get_offers(self, soup: BeautifulSoup, shop_id: int, link_data: LinkData) -> List[OfferData]:
        """Получить список оферов"""
        pass

    @abstractmethod
    def get_link_type(self, soup: BeautifulSoup, link: LinkData) -> LinkData:
        """Определить тип ссылки"""
        pass

    @abstractmethod
    def get_links(self, soup: BeautifulSoup, link: LinkData) -> List[LinkData]:
        """Возвращает список ссылок"""
        pass

    @abstractmethod
    def get_shops(self, soup: BeautifulSoup, link: LinkData) -> List[ShopData]:
        """Получить список магазинов"""
        pass

    def get_soup(self, url: str) -> BeautifulSoup:
        """Возвращает объект BeautifulSoup"""
        LOGGER.debug(f"Start {self.__class__}.scrape()")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        service = Service(executable_path=settings.CHROME_PATH)
        wd = webdriver.Chrome(options=chrome_options, service=service)
        wd.get(url)
        html = wd.page_source.replace('\n', '').replace('\r', '')
        wd.quit()
        soup = BeautifulSoup(html, 'lxml')
        return soup

    def get_robots(self, url: str) -> (Dict, bool):
        result = self._request(url)
        if result.status_code == 200:
            result_data_set = self._process_robots(result.content.decode())
            return result_data_set, True
        LOGGER.error(f"Error receiving robots.txt\n Url: {url}, \nresult: {result}. User-agent: {self.user_agent}")
        return dict(), False

    def get_urls_from_sitemap(self, sitemap_urls: List) -> Set:
        """Возвращает ссылки из sitemap"""
        result = set()
        for sitemap_url in sitemap_urls:
            resp = self._request(sitemap_url)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, features='xml')
                urls = self._process_sitemap(soup)
                for url in urls:
                    result.add(url.findNext("loc").text)
            else:
                LOGGER.error(f"Error receiving sitemap {resp}. User-agent: {self.user_agent}")
        return result

    def _process_robots(self, robots_txt: str) -> dict:
        """Обработать robots.txt"""
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

    def _request(self, url):
        if url.find('http') < 0:
            url = f'https://{url}'
        else:
            url = url.replace('http://', 'https://', 1)
        try:
            result = requests.get(url, headers=self.headers)
            if result.status_code == 200:
                return result
        except Exception as ex:
            LOGGER.warning(f"Error 1 attempt requests. Exception: {ex}")
        try:
            return requests.get(url, headers=self.headers, verify=False)
        except Exception as ex:
            LOGGER.warning(f"Error 2 attempt requests. Exception: {ex}")
            return False

    def _process_sitemap(self, soup: BeautifulSoup) -> list:
        """Рекурсивная функция обработки sitemap"""
        result_urls = list()
        sitemap_tags = soup.find_all("sitemap")
        for sitemap in sitemap_tags:
            url = sitemap.findNext("loc").text
            result = self._request(url)
            if result.status_code == 200:
                soup = BeautifulSoup(result.content, features='xml')
                result_urls.extend(self._process_sitemap(soup))
            else:
                LOGGER.error(f"Error receiving sitemap {result}. User-agent: {self.user_agent}")
        result_urls.extend(soup.find_all("url"))
        return result_urls


class Driver(BaseDriver):
    """Драйвер по умолчанию"""

    def get_offers(self, soup: BeautifulSoup, shop_id: int, link_data: LinkData) -> List[OfferData]:
        """Получить офферы"""
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
