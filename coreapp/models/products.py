from django.db import models

from coreapp.mixins.db import UpdatedMixin, CreatedMixin


class Brand(CreatedMixin, UpdatedMixin, models.Model):
    """ Бренды """
    name = models.CharField(verbose_name='Наименование', max_length=67, unique=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'


class Article(CreatedMixin, UpdatedMixin, models.Model):
    """ Артикул """
    art = models.CharField(verbose_name='Артикул', max_length=255)
    brand = models.ForeignKey(Brand, verbose_name='Бренд', related_name='articles')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Артикул'
        verbose_name_plural = 'Артикулы'


class Product(CreatedMixin, UpdatedMixin, models.Model):
    """ Товар """
    article = models.ForeignKey(Article, verbose_name='Артикул', related_name='products',
                                on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(verbose_name='Наименование', max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        unique_together = ("article", "name")
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Parameter(CreatedMixin, UpdatedMixin, models.Model):
    """ Параметры товаров """
    # warehouse = models.ForeignKey(Warehouse, verbose_name='Склад', null=True, blank=True, on_delete=models.CASCADE)
    # article = models.ForeignKey(Article, verbose_name='Артикул', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Наименование', max_length=63)
    value = models.CharField(verbose_name='Значение', max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Параметр товара'
        verbose_name_plural = 'Параметры товаров'
