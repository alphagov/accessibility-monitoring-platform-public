# Generated by Django 4.1.7 on 2023-05-12 07:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("audits", "0026_remove_audit_unpublished_report_data_updated_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="audit",
            name="accessibility_statement_deadline_not_complete_wording",
            field=models.TextField(
                blank=True,
                default="it includes a deadline of XXX for fixing XXX issues and this has not been completed",
            ),
        ),
        migrations.AddField(
            model_name="audit",
            name="accessibility_statement_deadline_not_sufficient_wording",
            field=models.TextField(
                blank=True,
                default="it includes a deadline of XXX for fixing XXX issues and this is not sufficient",
            ),
        ),
    ]
