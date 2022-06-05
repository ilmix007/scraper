from django.contrib import admin
from coreapp.models import Product, Article, Brand, Offer, Shop, Site, ParameterKey, SiteParameter
from coreapp.service.sites import SiteFacade
import logging

LOGGER = logging.getLogger(__name__)


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
    actions = ['read_robots']

    @staticmethod
    def read_robots(cls, request, queryset):
        for site in queryset:
            site_facade = SiteFacade(site)
            site_facade.read_robots()


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
