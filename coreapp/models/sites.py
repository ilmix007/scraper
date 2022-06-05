from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from coreapp.mixins.db import CreatedMixin, UpdatedMixin


class Site(CreatedMixin, UpdatedMixin, models.Model):
    name = models.CharField(verbose_name='Наименование', null=True, blank=True, max_length=127)
    url = models.URLField(verbose_name='url', unique=True, max_length=255)
    crawl_delay = models.IntegerField(verbose_name='Задержка обхода', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сайт'
        verbose_name_plural = 'Сайты'


class Shop(CreatedMixin, UpdatedMixin, models.Model):
    name = models.CharField(verbose_name='Наименование', unique=True, max_length=127)
    address = models.CharField(verbose_name='Адрес', unique=True, max_length=255)
    phone = PhoneNumberField(null=False, blank=False, unique=True)
    site = models.ForeignKey(Site, verbose_name='Сайт', related_name='shops', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'


class Url(CreatedMixin, UpdatedMixin, models.Model):
    link = models.URLField(verbose_name='Ссылка', max_length=255, unique=True)
    cite = models.ForeignKey(Site, verbose_name='Сайт', related_name='urls', on_delete=models.CASCADE)
    alt = models.CharField(verbose_name='Альтернативный текст', max_length=63, blank=True, null=True)
