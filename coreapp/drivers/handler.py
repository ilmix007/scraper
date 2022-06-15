from typing import List

from coreapp.drivers.base import BaseDriver, ScrapeResult
from coreapp.drivers.conf import DRIVER_CONF
from coreapp.service.sites import SiteFacade
import logging

LOGGER = logging.getLogger(__name__)
__all__ = ['Handler']


class Handler:
    def __init__(self, site: SiteFacade):
        self.site = site
        self.drive_class = self._get_drive_class()
        if self.drive_class:
            self.driver = self.drive_class()
        else:
            self.driver = BaseDriver()

    def _get_drive_class(self):
        return DRIVER_CONF.get(self.site.get_domain())

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
        try:
            result = self.driver.scrape(url)
            return True, result
        except Exception as ex:
            return False, ex
