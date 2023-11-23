# Generated by Django 4.2.4 on 2023-11-22 11:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0074_populate_enforcement_body_closed_case"),
    ]

    operations = [
        migrations.CreateModel(
            name="CaseStatus",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("", "All"),
                            ("unknown", "Unknown"),
                            ("unassigned-case", "Unassigned case"),
                            ("test-in-progress", "Test in progress"),
                            ("report-in-progress", "Report in progress"),
                            ("unassigned-qa-case", "Report ready to QA"),
                            ("qa-in-progress", "QA in progress"),
                            ("report-ready-to-send", "Report ready to send"),
                            ("in-report-correspondence", "Report sent"),
                            (
                                "in-probation-period",
                                "Report acknowledged waiting for 12-week deadline",
                            ),
                            (
                                "in-12-week-correspondence",
                                "After 12-week correspondence",
                            ),
                            ("reviewing-changes", "Reviewing changes"),
                            ("final-decision-due", "Final decision due"),
                            (
                                "case-closed-waiting-to-be-sent",
                                "Case closed and waiting to be sent to equalities body",
                            ),
                            (
                                "case-closed-sent-to-equalities-body",
                                "Case closed and sent to equalities body",
                            ),
                            (
                                "in-correspondence-with-equalities-body",
                                "In correspondence with equalities body",
                            ),
                            ("complete", "Complete"),
                            ("deactivated", "Deactivated"),
                        ],
                        default="unassigned-case",
                        max_length=200,
                    ),
                ),
                (
                    "case",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="status2",
                        to="cases.case",
                    ),
                ),
            ],
        ),
    ]