# Generated by Django 3.2.2 on 2021-06-04 09:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0009_auto_20210604_0854"),
    ]

    operations = [
        migrations.RenameField(
            model_name="case",
            old_name="website_compliant",
            new_name="is_website_compliant",
        ),
    ]
