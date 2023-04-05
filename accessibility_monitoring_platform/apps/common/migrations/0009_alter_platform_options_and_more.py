# Generated by Django 4.1a1 on 2022-07-07 14:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0008_auto_20220127_1444"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="platform",
            options={"verbose_name_plural": "Platform settings"},
        ),
        migrations.AddField(
            model_name="platform",
            name="report_viewer_accessibility_statement",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="platform",
            name="report_viewer_privacy_notice",
            field=models.TextField(blank=True, default=""),
        ),
    ]
