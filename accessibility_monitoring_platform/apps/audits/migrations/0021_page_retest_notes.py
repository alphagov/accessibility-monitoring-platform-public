# Generated by Django 4.1.2 on 2022-10-28 11:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "audits",
            "0020_audit_accessibility_statement_missing_mandatory_wording_notes",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="retest_notes",
            field=models.TextField(blank=True, default=""),
        ),
    ]
