# Generated by Django 4.0.2 on 2022-05-17 12:38

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0031_populate_pursuing"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="case",
            name="enforcement_body_interested",
        ),
        migrations.RemoveField(
            model_name="case",
            name="escalation_state",
        ),
    ]
