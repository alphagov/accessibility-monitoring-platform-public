# Generated by Django 4.0.2 on 2022-04-12 07:52

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0002_populate_report_templates"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="report",
            name="ready_for_qa",
        ),
    ]
