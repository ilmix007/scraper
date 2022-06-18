from typing import List

from bs4 import BeautifulSoup
from django.conf import settings
from coreapp.drivers.base import Driver, LinkData
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

    def scrape(self, url) -> bool:

        if settings.DEBUG:
            soup = self.driver.get_soup(url)
        else:
            try:
                soup = self.driver.get_soup(url)
            except Exception as ex:
                LOGGER.error(f'Failure scrape for {url.site.title}. Exception: {ex}')
                return False
        link_data = LinkData(url)
        link_data = self.driver.get_link_type(soup, link_data)
        if link_data.shop:
            shops = self.driver.get_shops(soup, link_data)
            self.site.update_shops(shopsdata=shops)
        if link_data.offer:
            offers = self.driver.get_offers(soup)
        links = self.driver.get_links(soup, link_data)

        return True
