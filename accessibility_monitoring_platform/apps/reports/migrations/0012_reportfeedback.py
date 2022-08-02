# Generated by Django 4.1rc1 on 2022-08-01 15:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0040_alter_case_status"),
        ("reports", "0011_reset_base_template_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReportFeedback",
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
                ("created", models.DateTimeField(auto_now_add=True)),
                ("guid", models.TextField(blank=True, default="")),
                (
                    "what_were_you_trying_to_do",
                    models.TextField(blank=True, default=""),
                ),
                ("what_went_wrong", models.TextField(blank=True, default="")),
                (
                    "case",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="cases.case",
                    ),
                ),
            ],
        ),
    ]
