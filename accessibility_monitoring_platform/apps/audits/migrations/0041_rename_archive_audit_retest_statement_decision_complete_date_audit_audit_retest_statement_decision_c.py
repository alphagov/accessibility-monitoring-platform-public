# Generated by Django 4.2.8 on 2024-01-31 09:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("audits", "0040_audit_initial_disproportionate_burden_claim_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="audit",
            old_name="archive_audit_retest_statement_decision_complete_date",
            new_name="audit_retest_statement_decision_complete_date",
        ),
        migrations.RenameField(
            model_name="audit",
            old_name="archive_audit_statement_decision_complete_date",
            new_name="audit_statement_decision_complete_date",
        ),
    ]