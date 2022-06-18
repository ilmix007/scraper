from datetime import datetime

from typing import List
from coreapp.drivers.base import ShopData, OfferData
from coreapp.models import Site, ParameterKey, SiteParameter, Link, Shop, City, Offer, Product, Brand, Parameter, \
    Article
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

    def get_shops(self):
        return self.site.shops.all()

    def update_offers(self, offers: List[OfferData]):
        for offer in offers:
            article, _ = Article.objects.get_or_create(art=offer.article.strip(),
                                                       defaults=dict(art=offer.article.strip()))
            if offer.brand:
                brand, _ = Brand.objects.get_or_create(name=offer.brand.strip(), defaults={'name': offer.brand.strip()})
                product, _ = Product.objects.get_or_create(brand=brand, article=article, defaults={
                    'brand': brand,
                    'article': article})
            else:
                product, _ = Product.objects.get_or_create(article=article, defaults={'article': article})
            for param in offer.parameters:
                Parameter.objects.get_or_create(name=param.name, value=param.value,
                                                defaults={'name': param.name, 'value': param.value})
            try:
                shop = Shop.objects.get(id=offer.shop_id)
            except Shop.DoesNotExist:
                LOGGER.error('Shop.DoesNotExist')
                continue
            link, _ = Link.objects.get_or_create(url=offer.link.url, defaults=dict(url=offer.link.url,
                                                                                   site=self.site,
                                                                                   alt=offer.link.alt.strip(),
                                                                                   last_processing=datetime.now()))
            offer_default = dict(product=product, shop=shop,
                                 name=offer.name.strip(), link=link,
                                 count=offer.count,
                                 price=offer.price)
            Offer.objects.get_or_create(product=product, shop=shop, defaults=offer_default)

    def update_shops(self, shopsdata: List[ShopData]):
        for shopdata in shopsdata:
            try:
                city = City.objects.get(name__iexact=shopdata.city)
            except (City.DoesNotExist, City.MultipleObjectsReturned):
                city = None
            obj, created = Shop.objects.update_or_create(site=self.site,
                                                         name=shopdata.name,
                                                         defaults={'address': shopdata.address.strip(),
                                                                   'phone': shopdata.phone.strip(),
                                                                   'city': city,
                                                                   'getparam': shopdata.shop_param.strip()})
            if created:
                LOGGER.info(f'Created shop{obj}')
            else:
                LOGGER.info(f'{obj} exists')
