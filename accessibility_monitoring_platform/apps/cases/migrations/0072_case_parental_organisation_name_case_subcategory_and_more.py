# Generated by Django 4.2.4 on 2023-11-01 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0018_subcategory"),
        ("cases", "0071_remove_case_accessibility_statement_notes_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="case",
            name="parental_organisation_name",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="case",
            name="subcategory",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="common.subcategory",
            ),
        ),
        migrations.AddField(
            model_name="case",
            name="website_name",
            field=models.TextField(blank=True, default=""),
        ),
    ]