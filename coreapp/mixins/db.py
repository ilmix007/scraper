from django.db import models


class BaseMixin(models.Model):
    """ Базовый класс миксинов """

    class Meta:
        abstract = True


class CreatedMixin(BaseMixin):
    """ Добавляет поле created """
    created = models.DateTimeField(verbose_name='Добавлен', auto_now_add=True)

    class Meta:
        abstract = True


class UpdatedMixin(BaseMixin):
    """ Добавляет поле updated """
    updated = models.DateTimeField(verbose_name='Изменен', auto_now=True)

    class Meta:
        abstract = True


class StartProcessMixin(BaseMixin):
    """ Добавляет поле start_process """
    start_process = models.DateTimeField(verbose_name='Начало обработки', null=True, blank=True)

    class Meta:
        abstract = True


class FinishProcessMixin(BaseMixin):
    """ Добавляет поле finish_process """
    finish_process = models.DateTimeField(verbose_name='Конец обработки', null=True, blank=True)

    class Meta:
        abstract = True


class LastProcessMixin(BaseMixin):
    """ Добавляет поле last_process """
    last_process = models.DateTimeField(verbose_name='Последняя обработка', null=True, blank=True)

    class Meta:
        abstract = True
