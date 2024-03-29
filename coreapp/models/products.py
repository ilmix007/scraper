from django.db import models

from coreapp.mixins.db import UpdatedMixin, CreatedMixin
from coreapp.models.sites import Shop, Link


class Brand(CreatedMixin, UpdatedMixin, models.Model):
    """ Бренды """
    name = models.CharField(verbose_name='Наименование', max_length=63, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'


class Article(CreatedMixin, UpdatedMixin, models.Model):
    """ Артикул """
    art = models.CharField(verbose_name='Артикул', max_length=255, unique=True)

    def __str__(self):
        return self.art

    class Meta:
        verbose_name = 'Артикул'
        verbose_name_plural = 'Артикулы'


class Product(CreatedMixin, UpdatedMixin, models.Model):
    """ Товар """
    brand = models.ForeignKey(Brand, verbose_name='Бренд', related_name='articles', blank=True, null=True,
                              on_delete=models.SET_NULL)
    article = models.ForeignKey(Article, verbose_name='Артикул', related_name='products',
                                on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(verbose_name='Наименование', max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.name} ({self.article} - {self.brand})'

    class Meta:
        ordering = ['name']
        unique_together = ('article', 'brand')
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Parameter(CreatedMixin, UpdatedMixin, models.Model):
    """ Параметр товара """
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Наименование', max_length=63)
    value = models.CharField(verbose_name='Значение', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Параметр товара'
        verbose_name_plural = 'Параметры товаров'


class Offer(CreatedMixin, UpdatedMixin, models.Model):
    """ Параметры товаров """
    product = models.ForeignKey(Product, verbose_name='Товар', related_name='offers', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Наименование', max_length=255, null=True, blank=True)
    shop = models.ForeignKey(Shop, verbose_name='Магазин', related_name='offers', on_delete=models.CASCADE)
    link = models.ForeignKey(Link, verbose_name='Ссылка', related_name='offers', on_delete=models.CASCADE)
    imgs = models.ManyToManyField(Link, verbose_name='Изображения', blank=True)
    count = models.IntegerField(verbose_name='Количество')
    price = models.FloatField(verbose_name='Цена')

    class Meta:
        unique_together = ('product', 'shop')
        verbose_name = 'Предложение'
        verbose_name_plural = 'Предложения'
