import time

from django.contrib import admin
from django.utils.html import format_html
from django.conf import settings
from coreapp.drivers.handler import Handler
from coreapp.models import Product, Article, Brand, Offer, Shop, Site, ParameterKey, SiteParameter, Link, Region, City
from django.contrib import messages
import logging

from coreapp.service.sites import SiteFacade

LOGGER = logging.getLogger(__name__)


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ['url', 'to_url', 'site', 'last_processing']
    search_fields = ['url']
    list_filter = ['site']
    raw_id_fields = ['site']

    def to_url(self, obj):
        return format_html('<a href="{}" target="_blank">ссылка</a>'.format(obj.url))

    actions = ['scrape']

    @admin.action(description='Парсить')
    def scrape(self, request, queryset):
        success_urls = list()
        fail_urls = list()
        for link in queryset:
            site_facade = SiteFacade(link.site)
            handler = Handler(site_facade)
            if handler.scrape(link.url):
                success_urls.append(link.site.title)
            else:
                fail_urls.append(link.site.title)
            time.sleep(site_facade.site.crawl_delay)

        if len(success_urls) > 0 and len(fail_urls) == 0:
            self.message_user(request, f"Успешно {len(success_urls)}", messages.SUCCESS)
        elif len(success_urls) == 0 and len(fail_urls) != 0:
            self.message_user(request, f"Ошибка {len(fail_urls)}", messages.ERROR)
        else:
            message = messages.WARNING
            self.message_user(request, f"Успешно {len(success_urls)}\n"
                                       f"Ошибка {len(fail_urls)} : {fail_urls}", message)


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
    search_fields = ['product__name', 'name']
    list_filter = ['product__brand', ('shop', admin.RelatedOnlyFieldListFilter)]
    raw_id_fields = ['product', 'shop', 'link', 'imgs']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'site', 'address', 'city', 'phone']
    search_fields = ['name', 'address', 'phone']
    raw_id_fields = ['site', 'city']
    list_filter = ['site', ('city', admin.RelatedOnlyFieldListFilter)]


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ['title', 'domain']
    search_fields = ['name', 'domain']
    actions = ['read_robots', 'read_sitemap', 'clear_urls']

    @admin.action(description='Прочитать robots.txt')
    def read_robots(self, request, queryset):
        success_sites = list()
        fail_sites = list()
        for site in queryset:
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
            self.message_user(request, f"Успешно прочитан(о) {len(success_sites)} robots.txt", messages.SUCCESS)
        elif len(success_sites) == 0 and len(fail_sites) != 0:
            self.message_user(request, f"Ошибка прочтения {len(fail_sites)} robots.txt", messages.ERROR)
        else:
            message = messages.WARNING
            self.message_user(request, f"Успешно прочитан(о) {len(success_sites)} robots.txt\n"
                                       f"Не прочитано {len(fail_sites)} : {fail_sites}", message)

    @admin.action(description='Прочитать sitemap')
    def read_sitemap(self, request, queryset):
        created, updated = 0, 0
        LOGGER.warning(f'Start read sitemap')
        for site in queryset:
            LOGGER.info(f'Start read sitemap {site.title}')
            site_facade = SiteFacade(site)
            handler = Handler(site_facade)
            try:
                created, updated = handler.read_sitemap()
            except Exception as ex:
                LOGGER.warning(f'Failure get sitemap for {site.title}. Exception {ex}')
        self.message_user(request, f"Created: {created}, updated: {updated}", messages.SUCCESS)

    @admin.action(description='Очистить ссылки сайта')
    def clear_urls(self, request, queryset):
        total_count = 0
        for site in queryset:
            site_facade = SiteFacade(site)
            deleted = site_facade.clear_urls()
            total_count += deleted[0]
        self.message_user(request, f"{total_count} entries deleted", messages.SUCCESS)


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


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'description']
    search_fields = ['name']
    list_filter = ['region']
    raw_id_fields = ['region']
