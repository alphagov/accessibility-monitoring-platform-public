# Generated by Django 3.2.4 on 2021-07-16 16:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0011_auto_20210716_1538"),
    ]

    operations = [
        migrations.RenameField(
            model_name="case",
            old_name="twelve_week_correspondance_notes",
            new_name="correspondance_notes",
        ),
    ]
