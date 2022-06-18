from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from coreapp.mixins.db import CreatedMixin, UpdatedMixin, StartProcessMixin, FinishProcessMixin
from urllib.parse import urlparse


class Link(CreatedMixin, UpdatedMixin, models.Model):
    url = models.URLField(verbose_name='Ссылка', max_length=255, unique=True)
    site = models.ForeignKey('coreapp.Site', verbose_name='Сайт', related_name='urls', on_delete=models.CASCADE)
    alt = models.CharField(verbose_name='Альтернативный текст', max_length=63, blank=True, null=True)
    last_processing = models.DateTimeField(verbose_name='Дата последней обработки', blank=True, null=True)

    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'

    def set_schema(self):
        self.link = self.url.replace('http://', 'https://', 1)

    @property
    def domain(self):
        return urlparse(self.link).netloc.replace('www.', '', 1)


class Site(CreatedMixin, UpdatedMixin, StartProcessMixin, FinishProcessMixin, models.Model):
    name = models.CharField(verbose_name='Наименование', null=True, blank=True, max_length=127)
    url = models.URLField(verbose_name='url', unique=True, max_length=255)
    crawl_delay = models.IntegerField(verbose_name='Задержка обхода', null=True, blank=True)
    DEFAULT_TIMEOUT = 0.5

    def __str__(self):
        return self.name if self.name else self.url

    @property
    def title(self):
        return self.name if self.name else self.url

    @property
    def timeout(self):
        if self.crawl_delay is None:
            return self.DEFAULT_TIMEOUT
        else:
            return self.crawl_delay

    class Meta:
        verbose_name = 'Сайт'
        verbose_name_plural = 'Сайты'

    def set_schema(self):
        self.url = self.url.replace('http://', 'https://', 1)


class ParameterKey(models.Model):
    title = models.CharField(verbose_name='Ключ', max_length=63, unique=True)

    class Meta:
        verbose_name = 'Ключ параметра сайта'
        verbose_name_plural = 'Ключи параметров сайтов'

    def __str__(self):
        return self.title


class SiteParameter(models.Model):
    key = models.ForeignKey(ParameterKey, verbose_name='Ключ', related_name='parameters', on_delete=models.CASCADE)
    value = models.CharField(verbose_name='Значение', max_length=255)
    site = models.ForeignKey(Site, verbose_name='Сaйт', related_name='parameters', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Параметр сайта'
        verbose_name_plural = 'Параметры сайтов'
        unique_together = ('key', 'value', 'site')

    def __str__(self):
        return f'{self.key}: {self.value} ({self.site})'


class Shop(CreatedMixin, UpdatedMixin, models.Model):
    name = models.CharField(verbose_name='Наименование', unique=True, max_length=127)
    address = models.CharField(verbose_name='Адрес', unique=True, max_length=255)
    phone = PhoneNumberField(null=True, blank=True, unique=True)
    site = models.ForeignKey(Site, verbose_name='Сайт', related_name='shops', on_delete=models.CASCADE)
    getparam = models.CharField(verbose_name='Get-параметр', max_length=63, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

