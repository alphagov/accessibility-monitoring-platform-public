# Generated by Django 4.1a1 on 2022-06-14 08:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0007_delete_publishedreport"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="reportwrapper",
            name="sub_header",
        ),
    ]
