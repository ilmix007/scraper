# Generated by Django 3.2.7 on 2022-06-17 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0004_alter_url_last_processing'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='getparam',
            field=models.CharField(blank=True, max_length=63, null=True, verbose_name='Get-параметр'),
        ),
        migrations.AddField(
            model_name='site',
            name='iterating',
            field=models.BooleanField(default=False, verbose_name='Парсить каждую страницу с разными параметрами'),
        ),
    ]
