# Generated by Django 3.2.7 on 2022-05-10 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coreapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='img',
            field=models.ManyToManyField(blank=True, to='coreapp.ImgLink', verbose_name='Изображения'),
        ),
        migrations.AlterField(
            model_name='product',
            name='img',
            field=models.ManyToManyField(blank=True, to='coreapp.ImgLink', verbose_name='Изображения'),
        ),
    ]
