# Generated by Django 3.2.7 on 2022-06-18 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0009_alter_site_crawl_delay'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='shop',
            unique_together={('site', 'getparam')},
        ),
    ]
