from django.apps import AppConfig


class CoreappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coreapp'
    verbose_name = 'Ядро'

    def ready(self):
        # Инициализация сигналов
        from . import signal_receivers



