# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-03 22:27
from __future__ import unicode_literals

from django.db import migrations, models

import fotopruvodce.photos.models
from fotopruvodce.core.text import MARKDOWN_HELP_TEXT


class Migration(migrations.Migration):

    dependencies = [
        ("photos", "0006_field_labels"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="content",
            field=models.TextField(blank=True, help_text=MARKDOWN_HELP_TEXT),
        ),
        migrations.AlterField(
            model_name="photo",
            name="description",
            field=models.TextField(
                blank=True, help_text=MARKDOWN_HELP_TEXT, verbose_name="Popis:"
            ),
        ),
        migrations.AlterField(
            model_name="photo",
            name="photo",
            field=models.ImageField(
                height_field="photo_height",
                help_text="Maximální povolené rozměry fotky jsou 1280×800px a velikost souboru do 2,5\xa0MB.",
                upload_to=fotopruvodce.photos.models.upload_photo_fullpath,
                validators=[fotopruvodce.photos.models.validate_photo],
                verbose_name="Fotka:",
                width_field="photo_width",
            ),
        ),
        migrations.AlterField(
            model_name="photo",
            name="thumbnail",
            field=models.ImageField(
                height_field="thumbnail_height",
                help_text="Maximální povolené rozměry náhledu jsou 300×300px a velikost souboru do 512,0\xa0KB.",
                upload_to=fotopruvodce.photos.models.upload_thumb_fullpath,
                validators=[fotopruvodce.photos.models.validate_thumbnail],
                verbose_name="Náhled:",
                width_field="thumbnail_width",
            ),
        ),
    ]
