# Generated by Django 3.2.4 on 2021-09-02 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0002_issuereport"),
    ]

    operations = [
        migrations.AddField(
            model_name="issuereport",
            name="complete",
            field=models.BooleanField(default=False),
        ),
    ]
