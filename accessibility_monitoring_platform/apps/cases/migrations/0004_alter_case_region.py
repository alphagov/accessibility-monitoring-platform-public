# Generated by Django 3.2.4 on 2021-07-05 15:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0001_initial"),
        ("cases", "0003_alter_case_website_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="case",
            name="region",
            field=models.ManyToManyField(blank=True, to="common.Region"),
        ),
    ]
