from datetime import datetime

from typing import List
from coreapp.drivers.base import ShopData, OfferData, LinkData
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
        """Создать ссылки по списку url-ов"""
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

    def create_links(self, links: List[LinkData]):
        """Создать ссылки по списку LinkData"""
        created = 0
        updated = 0
        for link in links:
            _, status = Link.objects.get_or_create(url=link.url, site=self.site,
                                                   defaults={'url': link.url, 'alt': link.alt, 'site': self.site})
            if status:
                created += 1
            else:
                updated += 1
        return created, updated

    def get_site_parameters(self, keys: list):
        """Получить параметры сайта"""
        keys = ParameterKey.objects.filter(title__in=keys)
        urls = list(self.site.parameters.filter(key__in=keys).values_list('value', flat=True))
        return urls

    def clear_urls(self):
        """Удалить все ссылки сайта"""
        return self.site.urls.all().delete()

    def get_shops(self):
        """Получить все магазины сайта"""
        return self.site.shops.all()

    def update_offers(self, offers: List[OfferData]):
        """Обновить предложения в БД"""
        for offer in offers:
            article_clean = offer.article.strip().lower().translate({ord(i): None for i in '+- @#$:;,./[]{}=()*|'})
            article, _ = Article.objects.get_or_create(art=article_clean, defaults=dict(art=article_clean))
            payload = {'article': article, 'name': offer.name.strip()}
            if offer.brand:
                brand, _ = Brand.objects.get_or_create(name=offer.brand.strip(), defaults={'name': offer.brand.strip()})
                payload.update({'brand': brand})
            product, _ = Product.objects.get_or_create(article=article, defaults=payload)
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
                                                         getparam=shopdata.shop_param.strip(),
                                                         defaults={'address': shopdata.address.strip(),
                                                                   'name': shopdata.name,
                                                                   'phone': shopdata.phone.strip(),
                                                                   'city': city,
                                                                   'getparam': shopdata.shop_param.strip()})
            if created:
                LOGGER.info(f'Created shop{obj}')
            else:
                LOGGER.info(f'{obj} exists')
