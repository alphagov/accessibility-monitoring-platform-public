# Generated by Django 5.1.3 on 2024-12-17 15:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0008_archive_pre_statement_check_cases"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CaseNoteHistory",
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
                    "note_type",
                    models.CharField(
                        choices=[
                            ("generic", "Generic"),
                            ("case-metadata", "Case metadata"),
                            ("initial-metadata", "Initial test metadata"),
                            ("manage-contacts", "Manage contacts"),
                            ("correspondence-notes", "Correspondence notes"),
                            ("12-week-cores-notes", "12-week correspondence notes"),
                            ("12-week-metadata", "12-week retest metadata"),
                            (
                                "post-case-notes",
                                "Summary of events after the case was closed",
                            ),
                            ("psb-appeal-notes", "Public sector body appeal notes"),
                            ("equality-body-notes", "Equality body notes"),
                        ],
                        default="generic",
                        max_length=100,
                    ),
                ),
                ("note", models.TextField(blank=True, default="")),
                ("created", models.DateTimeField(blank=True, null=True)),
                ("is_deleted", models.BooleanField(default=False)),
                (
                    "case",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="cases.case"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="case_note_entered_by_user",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Case note history",
                "ordering": ["-id"],
            },
        ),
    ]