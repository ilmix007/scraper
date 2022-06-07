from django.contrib import admin
from coreapp.drivers.driver import Driver
from coreapp.models import Product, Article, Brand, Offer, Shop, Site, ParameterKey, SiteParameter, Url
from django.contrib import messages
import logging

from coreapp.service.sites import SiteFacade

LOGGER = logging.getLogger(__name__)


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    list_display = ['link', 'site', 'last_processing']
    search_fields = ['link', 'site']
    list_filter = ['site']
    raw_id_fields = ['site']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['article', 'name', 'brand']
    search_fields = ['article', 'name', 'brand']
    list_filter = ['brand']
    raw_id_fields = ['article', ]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['art']
    search_fields = ['art']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ['product', 'shop', 'count', 'price']
    search_fields = ['product', 'shop']
    list_filter = ['product__brand']
    raw_id_fields = ['product', 'shop']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone']
    search_fields = ['name', 'address', 'phone']
    raw_id_fields = ['site']


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['title', 'url']
    search_fields = ['name', 'url']
    actions = ['read_robots', 'read_sitemap', 'clear_urls']

    @admin.action(description='Прочитать robots.txt')
    def read_robots(self, request, queryset):
        success_sites = list()
        fail_sites = list()
        for site in queryset:
            site_facade = SiteFacade(site)
            handler = Driver(site_facade)
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
        self.message_user(request, f"Успешно прочитан(о) {len(success_sites)} robots.txt {success_sites}\n"
                                   f"Не прочитано: {fail_sites}",
                          messages.SUCCESS)

    @admin.action(description='Прочитать sitemap')
    def read_sitemap(self, request, queryset):
        for site in queryset:
            site_facade = SiteFacade(site)
            handler = Driver(site_facade)
            handler.read_sitemap()

    @admin.action(description='Очистить ссылки сайта')
    def clear_urls(self, request, queryset):
        for site in queryset:
            site_facade = SiteFacade(site)
            site_facade.clear_urls()


@admin.register(SiteParameter)
class SiteParameterAdmin(admin.ModelAdmin):
    list_display = ['key', 'value', 'site']
    search_fields = ['key', 'site', 'value']
    raw_id_fields = ['key', 'site']
    list_filter = ['key', 'site']


@admin.register(ParameterKey)
class ParameterKeyAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
