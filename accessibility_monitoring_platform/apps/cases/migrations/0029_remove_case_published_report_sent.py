# Generated by Django 4.0.2 on 2022-04-25 14:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0028_case_published_report_sent"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="case",
            name="published_report_sent",
        ),
    ]
