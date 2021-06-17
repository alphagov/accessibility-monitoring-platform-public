# Generated by Django 3.2.4 on 2021-06-16 15:23

from django.db import migrations, models
import django.db.models.deletion

from accessibility_monitoring_platform.settings.base import UNDER_TEST


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DomainRegister",
            fields=[
                ("domain_id", models.IntegerField(primary_key=True, serialize=False)),
                ("domain_name", models.CharField(max_length=1000, unique=True)),
                ("organisation_id", models.IntegerField(blank=True, null=True)),
                (
                    "parent_domain",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                ("service", models.CharField(blank=True, max_length=1000, null=True)),
                (
                    "service_type",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                (
                    "registrant_email",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                (
                    "registrant_address",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                (
                    "registrant_postcode",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                ("nuts3", models.CharField(blank=True, max_length=5, null=True)),
                ("alexa_ranking", models.IntegerField(blank=True, null=True)),
                ("requires_authentication", models.BooleanField(blank=True, null=True)),
                (
                    "data_source",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                ("is_a_website", models.BooleanField(blank=True, null=True)),
                ("tempname", models.CharField(blank=True, max_length=1000, null=True)),
                ("domain_name_level", models.IntegerField(blank=True, null=True)),
                ("last_updated", models.DateTimeField(blank=True, null=True)),
            ],
            options={
                "db_table": "domain_register",
                "managed": UNDER_TEST,
            },
        ),
        migrations.CreateModel(
            name="HttpStatusCodes",
            fields=[
                (
                    "status",
                    models.CharField(max_length=3, primary_key=True, serialize=False),
                ),
                ("status_description", models.CharField(max_length=1000)),
                (
                    "status_type",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
            ],
            options={
                "db_table": "http_status_codes",
                "managed": UNDER_TEST,
            },
        ),
        migrations.CreateModel(
            name="NutsArea",
            fields=[
                (
                    "area_code",
                    models.CharField(
                        max_length=1000, primary_key=True, serialize=False
                    ),
                ),
                ("area_name", models.CharField(max_length=1000)),
                ("parent", models.CharField(blank=True, max_length=1000, null=True)),
                ("area_level", models.CharField(blank=True, max_length=5, null=True)),
            ],
            options={
                "db_table": "nuts_area",
                "managed": UNDER_TEST,
            },
        ),
        migrations.CreateModel(
            name="NutsConversion",
            fields=[
                (
                    "lad18cd",
                    models.CharField(
                        blank=True, db_column="LAD18CD", max_length=200, null=True
                    ),
                ),
                (
                    "lad18nm",
                    models.CharField(
                        blank=True, db_column="LAD18NM", max_length=200, null=True
                    ),
                ),
                (
                    "lau118cd",
                    models.CharField(
                        blank=True, db_column="LAU118CD", max_length=200, null=True
                    ),
                ),
                (
                    "lau118nm",
                    models.CharField(
                        blank=True, db_column="LAU118NM", max_length=200, null=True
                    ),
                ),
                (
                    "nuts318cd",
                    models.CharField(
                        blank=True, db_column="NUTS318CD", max_length=200, null=True
                    ),
                ),
                (
                    "nuts318nm",
                    models.CharField(blank=True, db_column="NUTS318NM", max_length=200),
                ),
                (
                    "nuts218cd",
                    models.CharField(
                        blank=True, db_column="NUTS218CD", max_length=200, null=True
                    ),
                ),
                (
                    "nuts218nm",
                    models.CharField(
                        blank=True, db_column="NUTS218NM", max_length=200, null=True
                    ),
                ),
                (
                    "nuts118cd",
                    models.CharField(
                        blank=True, db_column="NUTS118CD", max_length=200, null=True
                    ),
                ),
                (
                    "nuts118nm",
                    models.CharField(
                        blank=True, db_column="NUTS118NM", max_length=200, null=True
                    ),
                ),
                (
                    "fid",
                    models.IntegerField(
                        db_column="FID", primary_key=True, serialize=False
                    ),
                ),
            ],
            options={
                "db_table": "nuts_conversion",
                "managed": UNDER_TEST,
            },
        ),
        migrations.CreateModel(
            name="Organisation",
            fields=[
                (
                    "organisation_id",
                    models.IntegerField(primary_key=True, serialize=False),
                ),
                ("title", models.CharField(max_length=1000)),
                (
                    "abbreviation",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                ("own_website", models.BooleanField(blank=True, null=True)),
                ("format", models.CharField(blank=True, max_length=1000, null=True)),
                ("parent_id", models.IntegerField(blank=True, null=True)),
                ("last_updated", models.DateTimeField(blank=True, null=True)),
                ("street", models.CharField(blank=True, max_length=1000, null=True)),
                ("postcode", models.CharField(blank=True, max_length=10, null=True)),
                (
                    "temp_school_website",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
            ],
            options={
                "db_table": "organisation",
                "managed": UNDER_TEST,
            },
        ),
        migrations.CreateModel(
            name="OrganisationType",
            fields=[
                (
                    "organisation_type_id",
                    models.IntegerField(primary_key=True, serialize=False),
                ),
                ("type_name", models.CharField(max_length=1000)),
                (
                    "group_name",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
            ],
            options={
                "db_table": "organisation_type",
                "managed": UNDER_TEST,
            },
        ),
        migrations.CreateModel(
            name="Sector",
            fields=[
                ("sector_id", models.IntegerField(primary_key=True, serialize=False)),
                ("sector_name", models.CharField(max_length=1000)),
            ],
            options={
                "db_table": "sector",
                "managed": UNDER_TEST,
            },
        ),
        migrations.CreateModel(
            name="WebsiteRegister",
            fields=[
                (
                    "website_id",
                    models.IntegerField(primary_key=True, serialize=False, unique=True),
                ),
                ("url", models.CharField(max_length=1000)),
                ("service", models.CharField(blank=True, max_length=1000, null=True)),
                (
                    "htmlhead_title",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                (
                    "htmlmeta_description",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                ("last_updated", models.DateTimeField(blank=True, null=True)),
                (
                    "original_domain",
                    models.CharField(blank=True, max_length=1000, null=True),
                ),
                ("nuts3", models.CharField(blank=True, max_length=5, null=True)),
                ("requires_authentication", models.BooleanField(blank=True, null=True)),
                ("holding_page", models.BooleanField(blank=True, null=True)),
                (
                    "sector",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="websites.sector",
                    ),
                ),
            ],
            options={
                "db_table": "website_register",
                "managed": UNDER_TEST,
            },
        ),
        migrations.CreateModel(
            name="DomainsOrgs",
            fields=[
                (
                    "domain",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        primary_key=True,
                        serialize=False,
                        to="websites.domainregister",
                    ),
                ),
            ],
            options={
                "db_table": "domains_orgs",
                "managed": UNDER_TEST,
            },
        ),
        migrations.CreateModel(
            name="OrgOrgtype",
            fields=[
                (
                    "organisation",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        primary_key=True,
                        serialize=False,
                        to="websites.organisation",
                    ),
                ),
            ],
            options={
                "db_table": "org_orgtype",
                "managed": UNDER_TEST,
            },
        ),
        migrations.CreateModel(
            name="WebsitesOrgs",
            fields=[
                (
                    "website",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        primary_key=True,
                        serialize=False,
                        to="websites.websiteregister",
                    ),
                ),
            ],
            options={
                "db_table": "websites_orgs",
                "managed": UNDER_TEST,
            },
        ),
    ]
