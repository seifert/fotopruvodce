# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-28 23:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import fotopruvodce.photos.models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0005_thumbnail_filename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='active',
            field=models.BooleanField(db_index=True, default=True, verbose_name='Zobrazit v galerii:'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='deleted',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Smazáno:'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='description',
            field=models.TextField(blank=True, verbose_name='Popis:'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='photo',
            field=models.ImageField(height_field='photo_height', upload_to=fotopruvodce.photos.models.upload_photo_fullpath, verbose_name='Fotka:', width_field='photo_width'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='photo_height',
            field=models.PositiveIntegerField(verbose_name='Výška fotky:'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='photo_width',
            field=models.PositiveIntegerField(verbose_name='Šířka fotky:'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='section',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='photos.Section', verbose_name='Sekce:'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='thumbnail',
            field=models.ImageField(height_field='thumbnail_height', upload_to=fotopruvodce.photos.models.upload_thumb_fullpath, verbose_name='Náhled:', width_field='thumbnail_width'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='thumbnail_height',
            field=models.PositiveIntegerField(verbose_name='Výška náhledu:'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='thumbnail_width',
            field=models.PositiveIntegerField(verbose_name='Šířka náhledu:'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='timestamp',
            field=models.DateTimeField(verbose_name='Vloženo:'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='title',
            field=models.CharField(max_length=128, verbose_name='Název fotky:'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to=settings.AUTH_USER_MODEL, verbose_name='Autor:'),
        ),
    ]