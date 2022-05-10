from django.contrib import admin

from coreapp.models import Product, Article, Brand


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["article", "name"]
    search_fields = ["article", "name"]
    list_filter = ["article__brand"]
    raw_id_fields = ['article', ]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ["art", "brand"]
    search_fields = ["art", "brand"]
    list_filter = ["brand"]
    raw_id_fields = ['brand']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
