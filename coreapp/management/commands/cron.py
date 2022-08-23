from django.core.management.base import BaseCommand
from django.conf import settings
import time

from coreapp.models.sites import Site, Link
from coreapp.service.sites import SiteFacade
from coreapp.drivers.handler import Handler

import logging
LOGGER = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Парсинг robots.txt, sitemap и ссылок через планировщик задач"

    def handle(self, *args, **kwargs):
        success_sites = list()
        fail_sites = list()
        sites_generator = (item for item in Site.objects.all())
        for site in sites_generator:
            site_facade = SiteFacade(site)
            handler = Handler(site_facade)
            if settings.DEBUG:
                result = handler.read_robots()
            else:
                try:
                    result = handler.read_robots()
                except Exception as ex:
                    LOGGER.error(f'handler.read_robots(). Exception: {ex}')
                    fail_sites.append(site.title)
                    continue
            if result:
                success_sites.append(site.title)
            else:
                fail_sites.append(site.title)
                LOGGER.warning(f'Failure get robots.txt for {site.title}')
        if len(success_sites) > 0 and len(fail_sites) == 0:
            LOGGER.info(f"Успешно прочитан(о) {len(success_sites)} robots.txt")
        elif len(success_sites) == 0 and len(fail_sites) != 0:
            LOGGER.error(f"Ошибка прочтения {len(fail_sites)} robots.txt")
        else:
            LOGGER.warning(f"Успешно прочитан(о) {len(success_sites)} robots.txt\n"
                           f"Не прочитано {len(fail_sites)} : {fail_sites}")

        created, updated = 0, 0
        LOGGER.warning('Start read sitemap')
        sites_generator_sitemap = (item for item in Site.objects.all())
        for site in sites_generator_sitemap:
            LOGGER.info(f'Start read sitemap {site.title}')
            site_facade = SiteFacade(site)
            handler = Handler(site_facade)
            try:
                created, updated = handler.read_sitemap()
            except Exception as ex:
                LOGGER.warning(
                    f'Failure get sitemap for {site.title}. Exception {ex}')
        LOGGER.info(f"Created: {created}, updated: {updated}")

        success_urls = list()
        fail_urls = list()
        link_generator = (item for item in Link.objects.all())
        for link in link_generator:
            site_facade = SiteFacade(link.site)
            handler = Handler(site_facade)
            if handler.scrape(link.url):
                success_urls.append(link.site.title)
            else:
                fail_urls.append(link.site.title)
            time.sleep(site_facade.site.crawl_delay)

        if len(success_urls) > 0 and len(fail_urls) == 0:
            LOGGER.info(f"Успешно {len(success_urls)}")
        elif len(success_urls) == 0 and len(fail_urls) != 0:
            LOGGER.error(f"Ошибка {len(fail_urls)}")
        else:
            LOGGER.warning(f"Успешно {len(success_urls)}\n"
                           f"Ошибка {len(fail_urls)} : {fail_urls}")
