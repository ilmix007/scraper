import os
import time
from abc import ABC, abstractmethod
from random import randint
from typing import List, Dict, Set
from urllib.error import URLError
from urllib.parse import ParseResult

from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import logging
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import urllib.robotparser
import urllib.request
from coreapp.drivers.user_agents import USER_AGENTS
from django.conf import settings
from dataclasses import dataclass

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
        # user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) \
        # Chrome/60.0.3112.50 Safari/537.36'
        chrome_options.add_argument(f'user-agent={self.user_agent}')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--Accept=*/*')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--Sec-Fetch-Dest=empty')
        chrome_options.add_argument('--Sec-Fetch-Mode=cors')
        chrome_options.add_argument('--Sec-Fetch-Site=same-site')
        chrome_options.add_argument('--Connection=keep-alive')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--accept-language=ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7")
        chrome_options.add_argument("--enable-javascript")
        # chrome_options.add_argument("javascript.enabled", True)

        # userProfile = "/home/ilmix/.config/google-chrome/Default"
        # chrome_options.add_argument("user-data-dir={}".format(userProfile))

        # chrome_options.add_argument('--headless')
        # chrome_options.headless = True
        # chrome_options.add_argument("--enable-javascript")
        service = Service(executable_path=settings.CHROME_PATH)
        wd = webdriver.Chrome(options=chrome_options, service=service)
        # wd.get('https://ya.ru')
        # handle = wd.current_window_handle
        # wd.service.stop()
        # time.sleep(6)
        # wd = webdriver.Chrome(options=chrome_options, service=service)
        # wd.switch_to.window(handle)
        wd.get(url)
        time.sleep(1)
        wd.refresh()
        html = wd.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        html = html.replace('\n', '').replace('\r', '')
        wd.quit()
        soup = BeautifulSoup(html, 'lxml')
        return soup

    def get_robots(self, url: ParseResult) -> Dict:
        result = dict()
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(url.geturl())
        print(url.geturl())
        try:
            rp.read()
        except URLError:
            url_str = f'https://{url.netloc}/robots.txt'
            print(url_str)
            resp = self._request(url_str)
            if resp.status_code == 200:
                robots_txt = resp.content.decode()
                robots_txt = robots_txt.replace('\r', '')
                robots_txt = robots_txt.replace('\t', '')
                rp.parse(robots_txt.splitlines())
        rrate = rp.request_rate("*")
        if rrate is not None:
            result.update({'Request-rate': [rrate.seconds]})
        if rp.crawl_delay("*") is not None:
            result.update({'Crawl-delay': [rp.crawl_delay("*")]})
            print(rp.site_maps())
        if isinstance(rp.site_maps(), list):
            result.update({'Sitemap': rp.site_maps()})
        elif isinstance(rp.site_maps(), str):
            result.update({'Sitemap': [rp.site_maps()]})
        # else:
        print(result)
        return result

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

    # def _process_robots(self, robots_txt: str) -> dict:
    #     """Обработать robots.txt"""
    #
    #     result_data_set = dict()
    #     robots_txt = robots_txt.replace('\r', '')
    #     robots_txt = robots_txt.replace('\t', '')
    #     robots_arr = robots_txt.split()
    #     if len(robots_arr) > 0:
    #         if len(robots_arr[0]) > 30 and len(robots_arr) < 2:
    #             for item in settings.ROBOT_KEYS:
    #                 robots_txt = robots_txt.replace(f' {item}', f'\n{item}')
    #     for line in robots_txt.split("\n"):
    #         if len(line) > 0:
    #             if line[0] != '#':
    #                 robots_txt = robots_txt.replace('\r', '')
    #                 key = line.split(':')[0].split(' ')[0]
    #                 print(key)
    #                 value = line.split(':')[1].split(' ')[0]
    #                 print(value)
    #                 if key not in result_data_set.keys():
    #                     result_data_set[key] = list()
    #                 result_data_set[key].append(value)
    #     return result_data_set

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
