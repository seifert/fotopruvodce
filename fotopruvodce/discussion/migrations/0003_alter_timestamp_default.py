# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-14 21:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('discussion', '0002_comment_add_thread_and_level'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='timestamp',
            field=models.DateTimeField(),
        ),
    ]
