from django.contrib import admin
from coreapp.drivers.driver import Driver
from coreapp.models import Product, Article, Brand, Offer, Shop, Site, ParameterKey, SiteParameter, Url
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

    def read_robots(self, request, queryset):
        for site in queryset:
            site_facade = SiteFacade(site)
            handler = Driver(site_facade)
            handler.read_robots()

    def read_sitemap(self, request, queryset):
        for site in queryset:
            site_facade = SiteFacade(site)
            handler = Driver(site_facade)
            handler.read_sitemap()

    def clear_urls(self, request, queryset):
        for site in queryset:
            site_facade = SiteFacade(site)
            site_facade.clear_urls()

    read_robots.short_description = 'Прочитать robots.txt'
    read_sitemap.short_description = 'Прочитать sitemap'
    clear_urls.short_description = 'Очистить ссылки сайта'


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
