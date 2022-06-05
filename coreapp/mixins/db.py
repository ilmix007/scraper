from django.db import models


class BaseMixin(models.Model):
    """ Базовый класс миксинов """

    class Meta:
        abstract = True


class CreatedMixin(BaseMixin):
    """ Добавляет поле created """
    created = models.DateTimeField(verbose_name='Добавлен', auto_now_add=True)


class UpdatedMixin(BaseMixin):
    """ Добавляет поле updated """
    updated = models.DateTimeField(verbose_name='Изменен', auto_now=True)


class StartProcessMixin(BaseMixin):
    """ Добавляет поле last_process """
    start_process = models.DateTimeField(verbose_name='Начало обработки')


class FinishProcessMixin(BaseMixin):
    """ Добавляет поле finish_process """
    finish_process = models.DateTimeField(verbose_name='Конец обработки')


class LastProcessMixin(BaseMixin):
    """ Добавляет поле last_process """
    last_process = models.DateTimeField(verbose_name='Последняя обработка')
