# Generated by Django 3.2.7 on 2021-09-30 16:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="notificationssettings",
            options={
                "verbose_name": "NotificationSetting",
                "verbose_name_plural": "NotificationSettings",
            },
        ),
        migrations.RenameField(
            model_name="notifications",
            old_name="endpoint",
            new_name="path",
        ),
    ]
