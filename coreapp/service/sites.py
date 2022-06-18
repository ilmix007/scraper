from typing import List

from coreapp.drivers.base import ShopData
from coreapp.models import Site, ParameterKey, SiteParameter, Link, Shop, City
from urllib.parse import urlparse
import logging

LOGGER = logging.getLogger(__name__)


class SiteFacade:
    """Фасад для работы с сайтом"""

    def __init__(self, site: Site):
        self.site = site
        self.domain = site.domain

    def set_params(self, key, values: list):
        key, _ = ParameterKey.objects.get_or_create(title=key, defaults={'title': key})
        key.save()
        if key.title == 'Clean-param':
            for value in values:
                vals = value.split('&')
                for val in vals:
                    param, _ = SiteParameter.objects.get_or_create(key=key, value=val, site=self.site,
                                                                   defaults={'key': key, 'value': val,
                                                                             'site': self.site})
        else:
            for val in values:
                param, _ = SiteParameter.objects.get_or_create(key=key, value=val, site=self.site,
                                                               defaults={'key': key, 'value': val, 'site': self.site})

    def create_urls(self, urlset):
        created = 0
        updated = 0
        for url in urlset:
            _, status = Link.objects.get_or_create(url=url,
                                                   site=self.site,
                                                   defaults={'url': url, 'site': self.site})
            if status:
                created += 1
            else:
                updated += 1
        return created, updated

    def get_urls(self, keys: list):
        keys = ParameterKey.objects.filter(title__in=keys)
        urls = list(self.site.parameters.filter(key__in=keys).values_list('value', flat=True))
        return urls

    def clear_urls(self):
        return self.site.urls.all().delete()

    def update_shops(self, shopsdata: List[ShopData]):
        for shopdata in shopsdata:
            try:
                city = City.objects.get(name__iexact=shopdata.city)
            except City.DoesNotExist:
                city = None
            obj, created = Shop.objects.update_or_create(site=self.site,
                                                         name=shopdata.name,
                                                         defaults={'address': shopdata.address,
                                                                   'phone': shopdata.phone,
                                                                   'city': city,
                                                                   'getparam': shopdata.shop_param})
            if created:
                LOGGER.info(f'Created shop{obj}')
            else:
                LOGGER.info(f'{obj} exists')
