# Generated by Django 4.2.8 on 2023-12-27 10:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cases", "0078_alter_casestatus_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="case",
            name="cores_overview_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="case",
            name="find_contact_details_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="case",
            name="four_week_followup_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="case",
            name="one_week_followup_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="case",
            name="one_week_followup_final_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="case",
            name="report_acknowledged_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="case",
            name="report_sent_on_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="case",
            name="twelve_week_update_request_ack_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="case",
            name="twelve_week_update_requested_complete_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]