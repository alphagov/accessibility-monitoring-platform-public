# Generated by Django 3.2.2 on 2021-06-02 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cases", "0005_auto_20210602_0856"),
    ]

    operations = [
        migrations.AddField(
            model_name="contact",
            name="detail",
            field=models.CharField(default="", max_length=200),
        ),
    ]
