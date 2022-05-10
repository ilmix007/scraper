from django.contrib import admin

from coreapp.models import Product, Article, Brand, Offer, Shop


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['article', 'name']
    search_fields = ['article', 'name']
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
    list_display = ['product', 'shop', 'count']
    search_fields = ['product', 'shop']
    list_filter = ['product__brand']
    raw_id_fields = ['product', 'shop']


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'phone']
    search_fields = ['name', 'address', 'phone']
    raw_id_fields = ['site']
