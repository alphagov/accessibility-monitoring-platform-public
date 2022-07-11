# Generated by Django 4.1a1 on 2022-07-11 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0009_alter_platform_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChangeToPlatform",
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
                ("name", models.CharField(max_length=200)),
                ("notes", models.TextField(blank=True, default="")),
                ("created", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name_plural": "changes to platform",
                "ordering": ["-id"],
            },
        ),
    ]
