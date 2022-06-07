from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from coreapp.models import Site


@receiver([pre_save], sender=Site)
def clear_file_report(sender, instance: Site, **kwargs):
    instance.set_schema()
