# Generated by Django 3.2.7 on 2022-06-07 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0003_alter_url_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='url',
            name='last_processing',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата последней обработки'),
        ),
    ]
