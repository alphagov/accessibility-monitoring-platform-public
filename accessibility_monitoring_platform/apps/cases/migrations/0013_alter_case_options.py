# Generated by Django 3.2.8 on 2021-10-20 08:49

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0012_auto_20210922_0814"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="case",
            options={"ordering": ["-id"]},
        ),
    ]
