from typing import List

from bs4 import BeautifulSoup
from django.conf import settings
from coreapp.drivers.base import Driver, ScrapeResult, LinkData
from coreapp.drivers.conf import DRIVER_CONF
from coreapp.service.sites import SiteFacade
import logging

LOGGER = logging.getLogger(__name__)
__all__ = ['Handler']


class Handler:
    def __init__(self, site: SiteFacade):
        self.site = site
        drive_class = DRIVER_CONF.get(self.site.get_domain())
        if drive_class:
            self.driver = drive_class()
        else:
            self.driver = Driver()

    def read_robots(self) -> bool:
        url = f'{self.site.url}/robots.txt'
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

    def scrape(self, url) -> (bool, List[ScrapeResult] or Exception):

        if settings.DEBUG:
            soup = self.driver.get_soup(url)
        else:
            try:
                result = self.driver.get_soup(url)
                return True, result
            except Exception as ex:
                return False, ex
        link = LinkData(url)
        link = self.driver.get_link_type(soup, link)
        if link.shop:
            shops = self.driver.get_shops(soup, link)
        else:
            shops = list()
        if link.offer:
            offer = self.driver.get_offer(soup)
            offers = [offer]
        else:
            offers = list()
        links = self.driver.get_links(soup, link)
        result = ScrapeResult(offers=offers, shops=shops, links=links)
        return True, result
