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


class StartProcessMixin(models.Model):
    """ Добавляет поле start_process """
    start_process = models.DateTimeField(verbose_name='Начало обработки', null=True, blank=True)

    class Meta:
        abstract = True


class FinishProcessMixin(models.Model):
    """ Добавляет поле finish_process """
    finish_process = models.DateTimeField(verbose_name='Конец обработки', null=True, blank=True)

    class Meta:
        abstract = True


class LastProcessMixin(models.Model):
    """ Добавляет поле last_process """
    last_process = models.DateTimeField(verbose_name='Последняя обработка', null=True, blank=True)

    class Meta:
        abstract = True
