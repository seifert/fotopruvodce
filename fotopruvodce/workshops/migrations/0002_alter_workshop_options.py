# Generated by Django 5.1.1 on 2024-09-22 10:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("workshops", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="workshop",
            options={"ordering": ["-timestamp"]},
        ),
    ]
