# Generated by Django 4.0.2 on 2022-04-25 07:48

from django.db import migrations


REPORT_WRAPPER_TEXT = {
    "title": "Accessibility report for {{ report.case.domain }}",
    "title_caption": "Accessibility report",
    "sub_header": "",
    "sent_by": "[Government Digital Service](https://www.gov.uk/government/organisations/government-digital-service)",
    "contact": "[accessibility-monitoring@digital.cabinet-office.gov.uk](mailto:accessibility-monitoring@digital.cabinet-office.gov.uk)",
    "related_content": """
* [Understanding accessibility requirements for public sector bodies](https://www.gov.uk/guidance/accessibility-requirements-for-public-sector-websites-and-apps)
* [Make your website or app accessible and publish an accessibility statement](https://www.gov.uk/guidance/make-your-website-or-app-accessible-and-publish-an-accessibility-statement)
* [Public sector website and mobile application accessibility monitoring](https://www.gov.uk/guidance/public-sector-website-and-mobile-application-accessibility-monitoring)
* [Accessibility monitoring: How we test](https://www.gov.uk/guidance/accessibility-monitoring-how-we-test)
    """,
}


def populate_report_wrapper(apps, schema_editor):  # pylint: disable=unused-argument
    ReportWrapper = apps.get_model("reports", "ReportWrapper")
    ReportWrapper.objects.create(**REPORT_WRAPPER_TEXT)


def reverse_code(apps, schema_editor):  # pylint: disable=unused-argument
    ReportWrapper = apps.get_model("reports", "ReportWrapper")
    ReportWrapper.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("reports", "0005_reportwrapper_alter_report_report_version"),
    ]

    operations = [
        migrations.RunPython(populate_report_wrapper, reverse_code=reverse_code),
    ]
