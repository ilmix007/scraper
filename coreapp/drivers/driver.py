from coreapp.drivers.base import BaseDriver
from coreapp.drivers.conf import DRIVER_CONF
from coreapp.service.sites import SiteFacade
import logging

LOGGER = logging.getLogger(__name__)
__all__ = ['Driver']


class Driver:
    def __init__(self, site: SiteFacade):
        self.site = site
        self.drive_class = self._get_drive_class()
        if self.drive_class:
            self.driver = self.drive_class()
        else:
            self.driver = BaseDriver()

    def _get_drive_class(self):
        return DRIVER_CONF.get(self.site.get_domain())

    def read_robots(self):
        url = f'{self.site.url}/robots.txt'
        result_data_set, status = self.driver.get_robots(url)
        if status:
            for key, values in result_data_set.items():
                self.site.set_params(key, values)
            return True
        return False

    def read_sitemap(self):
        sitemap_urls = list(self.site.get_urls(['Sitemap', 'sitemap']))
        urls = self.driver.get_urls_from_sitemap(sitemap_urls)
        self.site.create_urls(urls)
