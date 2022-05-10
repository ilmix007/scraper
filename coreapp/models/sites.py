from django.db import models


class Shop(models.Model):
    name = models.CharField(verbose_name='Наименование', unique=True, max_length=127)
    created = models.DateTimeField(verbose_name='Дата добавления', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='Последнее изменение', auto_now=True)


class Region(models.Model):
    """Регион"""
    name = models.CharField(verbose_name='Наименование', max_length=128, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'


class City(models.Model):
    """ Город """

    name = models.CharField(verbose_name='Наименование', max_length=63)
    region = models.ForeignKey(Region, verbose_name='Регион', related_name='cities', on_delete=models.PROTECT)
    lat = models.IntegerField(verbose_name='Широта', null=True, blank=True)
    long = models.IntegerField(verbose_name='Долгота', null=True, blank=True)

    class Meta:
        unique_together = ("name", "region")
        verbose_name = 'Город'
        verbose_name_plural = 'Города'
        ordering = ['name']

    @property
    def region_name(self):
        return str(self.region.name)

    def __str__(self):
        return self.name
