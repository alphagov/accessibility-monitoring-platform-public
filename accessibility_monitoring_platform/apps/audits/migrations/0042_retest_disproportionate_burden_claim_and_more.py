# Generated by Django 4.2.10 on 2024-02-29 10:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "audits",
            "0041_rename_archive_audit_retest_statement_decision_complete_date_audit_audit_retest_statement_decision_c",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="retest",
            name="disproportionate_burden_claim",
            field=models.CharField(
                choices=[
                    ("no-assessment", "Claim with no assessment"),
                    ("assessment", "Claim with assessment"),
                    ("no-claim", "No claim"),
                    ("not-checked", "Not checked"),
                ],
                default="not-checked",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="retest",
            name="disproportionate_burden_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="retest",
            name="disproportionate_burden_notes",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="retest",
            name="statement_compliance_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="retest",
            name="statement_compliance_notes",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="retest",
            name="statement_compliance_state",
            field=models.CharField(
                choices=[
                    ("compliant", "Compliant"),
                    ("not-compliant", "Not compliant"),
                    ("unknown", "Not assessed"),
                ],
                default="unknown",
                max_length=200,
            ),
        ),
        migrations.AddField(
            model_name="retest",
            name="statement_custom_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="retest",
            name="statement_decision_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="retest",
            name="statement_feedback_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="retest",
            name="statement_non_accessible_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="retest",
            name="statement_overview_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="retest",
            name="statement_pages_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="retest",
            name="statement_preparation_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="retest",
            name="statement_results_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="retest",
            name="statement_website_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="RetestStatementCheckResult",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("overview", "Statement overview"),
                            ("website", "Statement information"),
                            ("compliance", "Compliance status"),
                            ("non-accessible", "Non-accessible content"),
                            ("preparation", "Statement preparation"),
                            ("feedback", "Feedback and enforcement procedure"),
                            ("custom", "Custom statement issues"),
                        ],
                        default="custom",
                        max_length=20,
                    ),
                ),
                (
                    "check_result_state",
                    models.CharField(
                        choices=[
                            ("yes", "Yes"),
                            ("no", "No"),
                            ("not-tested", "Not tested"),
                        ],
                        default="not-tested",
                        max_length=10,
                    ),
                ),
                ("comment", models.TextField(blank=True, default="")),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "retest",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="audits.retest"
                    ),
                ),
                (
                    "statement_check",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="audits.statementcheck",
                    ),
                ),
            ],
            options={
                "ordering": ["statement_check__position", "id"],
            },
        ),
    ]
