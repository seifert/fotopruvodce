# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-05-20 12:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("discussion", "0005_markdown_help_text"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="ip",
        ),
    ]
