# Generated by Django 3.2.2 on 2021-06-04 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0012_auto_20210604_1347'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='archived',
            field=models.BooleanField(default=False),
        ),
    ]
