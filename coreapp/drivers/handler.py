import time
from typing import List

from bs4 import BeautifulSoup
from django.conf import settings
from coreapp.drivers.base import Driver, LinkData, ShopData
from coreapp.drivers.conf import DRIVER_CONF
from coreapp.service.sites import SiteFacade
import logging

LOGGER = logging.getLogger(__name__)
__all__ = ['Handler']


class Handler:
    def __init__(self, site: SiteFacade):
        self.site = site
        drive_class = DRIVER_CONF.get(self.site.domain)
        if drive_class:
            self.driver = drive_class()
        else:
            self.driver = Driver()

    def read_robots(self) -> bool:
        url = f'{self.site.domain}/robots.txt'
        result_data_set, status = self.driver.get_robots(url)
        if status:
            for key, values in result_data_set.items():
                self.site.set_params(key, values)
            return True
        return False

    def read_sitemap(self):
        created, updated = 0, 0
        sitemap_urls = list(self.site.get_urls(['Sitemap', 'sitemap']))
        urls = self.driver.get_urls_from_sitemap(sitemap_urls)
        if urls:
            created, updated = self.site.create_urls(urls)
        return created, updated

    def get_soup(self, url):
        if settings.DEBUG:
            soup = self.driver.get_soup(url)
        else:
            try:
                soup = self.driver.get_soup(url)
            except Exception as ex:
                LOGGER.error(f'Failure scrape for {url}. Exception: {ex}')
                return False
        return soup

    def scrape(self, url) -> bool:
        shops = self.site.get_shops()
        if shops.count() == 0:
            soup = self.get_soup(url)
            if soup is False:
                return False
            link_data = LinkData(url)
            link_data = self.driver.get_link_type(soup, link_data)
            if link_data.shop:
                shopsdata = self.driver.get_shops(soup, link_data)
                self.site.update_shops(shopsdata=shopsdata)
                shops = self.site.get_shops()

        for shop in shops:
            local_url = f'{url}{shop.getparam}'
            # shop_data = ShopData(name=shop.name, city=shop.city, address=shop.address, phone=shop.address,
            #                      url=local_url, shop_param=shop.getparam)
            soup = self.get_soup(local_url)
            if soup is False:
                return False
            link_data = LinkData(url)
            self._process_soup(soup, link_data=link_data, shop_id=shop.id)
            # if settings.DEBUG:
            #     break
            time.sleep(self.site.site.crawl_delay)
        return True

    def _process_soup(self, soup, link_data, shop_id):
        link_data = self.driver.get_link_type(soup, link_data)
        if link_data.shop:
            shopsdata = self.driver.get_shops(soup, link_data)
            self.site.update_shops(shopsdata=shopsdata)
        if link_data.offer:
            offers = self.driver.get_offers(soup, shop_id, link_data)
            self.site.update_offers(offers=offers)
        links = self.driver.get_links(soup, link_data)
        created, updated = self.site.create_links(links)
        LOGGER.info(f'Created: {created} link(s). Updated {updated} link(s)')
