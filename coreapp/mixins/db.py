from django.db import models


class CreatedMixin(models.Model):
    """ Добавляет поле created """
    created = models.DateTimeField(verbose_name='Добавлен', auto_now_add=True)

    class Meta:
        abstract = True


class UpdatedMixin(models.Model):
    """ Добавляет поле updated """
    updated = models.DateTimeField(verbose_name='Изменен', auto_now=True)

    class Meta:
        abstract = True
