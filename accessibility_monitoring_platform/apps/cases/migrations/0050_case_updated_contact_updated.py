# Generated by Django 4.1.4 on 2023-03-13 10:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0049_case_enforcement_retest_document_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="case",
            name="updated",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="contact",
            name="updated",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]