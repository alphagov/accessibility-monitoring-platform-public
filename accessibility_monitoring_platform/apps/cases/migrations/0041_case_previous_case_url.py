# Generated by Django 4.1 on 2022-08-16 07:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0040_alter_case_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="case",
            name="previous_case_url",
            field=models.TextField(blank=True, default=""),
        ),
    ]
