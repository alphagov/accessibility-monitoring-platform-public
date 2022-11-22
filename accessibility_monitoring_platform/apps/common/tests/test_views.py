"""
Tests for common views
"""
from datetime import datetime, timezone
import pytest
from unittest.mock import patch

from pytest_django.asserts import assertContains, assertNotContains

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse

from ...audits.models import Audit
from ...cases.models import Case, RECOMMENDATION_NO_ACTION
from ..models import Platform
from ..utils import get_platform_settings

EMAIL_SUBJECT: str = "Email subject"
EMAIL_MESSAGE: str = "Email message"
ISSUE_REPORT_LINK: str = """<a href="/common/report-issue/?page_url=/"
target="_blank"
class="govuk-link govuk-link--no-visited-state">report</a>"""
CASE_METRIC_OVER_THIS_MONTH: str = """<p id="{metric_id}" class="govuk-body-m">
    <span class="govuk-!-font-size-48"><b>{number_this_month}</b></span>
    <svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="40" height="40"
        stroke="currentColor" stroke-width="3" fill="none">
            <line x1="20" y1="5" x2="20" y2="35"/>
            <line x1="20" y1="5" x2="30" y2="10"/>
            <line x1="20" y1="5" x2="10" y2="10"/>
        </svg>
    Projected {percentage_difference}% over December ({number_last_month} {lowercase_label})
</p>"""
CASE_METRIC_UNDER_THIS_MONTH: str = """<p id="{metric_id}" class="govuk-body-m">
    <span class="govuk-!-font-size-48"><b>{number_this_month}</b></span>
    <svg aria-hidden="true" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="40" height="40"
        stroke="currentColor" stroke-width="3" fill="none">
            <line x1="20" y1="5" x2="20" y2="35"/>
            <line x1="20" y1="35" x2="30" y2="30"/>
            <line x1="20" y1="35" x2="10" y2="30"/>
    </svg>
    Projected {percentage_difference}% under December ({number_last_month} {lowercase_label})
</p>"""
CASE_METRIC_YEARLY_TABLE: str = """<table id="{table_id}" class="govuk-table">
    <thead class="govuk-table__head">
        <tr class="govuk-table__row">
            <th scope="col" class="govuk-table__header govuk-!-width-one-third">Month</th>
            <th scope="col" class="govuk-table__header govuk-!-width-one-third">Count</th>
        </tr>
    </thead>
    <tbody class="govuk-table__body">

            <tr class="govuk-table__row">
                <td class="govuk-table__cell">
                    November 2021
                </td>
                <td class="govuk-table__cell">1</td>
            </tr>

            <tr class="govuk-table__row">
                <td class="govuk-table__cell">
                    December 2021
                </td>
                <td class="govuk-table__cell">2</td>
            </tr>

            <tr class="govuk-table__row">
                <td class="govuk-table__cell">
                    January 2022
                </td>
                <td class="govuk-table__cell">1</td>
            </tr>

    </tbody>
</table>"""
POLICY_PROGRESS_METRIC: str = """<p id="{id}" class="govuk-body-m">
    <span class="govuk-!-font-size-48 amp-padding-right-20"><b>{percentage}%</b></span>
    {partial_count} out of {total_count}
</p>"""


@pytest.mark.parametrize(
    "url_name,expected_header",
    [
        ("common:contact-admin", "Contact admin"),
        ("common:edit-active-qa-auditor", ">Active QA auditor</h1>"),
        ("common:platform-history", ">Platform version history</h1>"),
        ("common:issue-report", ">Report an issue</h1>"),
        ("common:accessibility-statement", ">Accessibility statement</h1>"),
        ("common:privacy-notice", ">Privacy notice</h1>"),
        ("common:markdown-cheatsheet", ">Markdown cheatsheet</h1>"),
        ("common:metrics-case", ">Case metrics</h1>"),
        ("common:metrics-policy", ">Policy metrics</h1>"),
    ],
)
def test_page_renders(url_name, expected_header, admin_client):
    """Test common page is rendered"""
    response: HttpResponse = admin_client.get(reverse(url_name))

    assert response.status_code == 200
    assertContains(response, expected_header)


@pytest.mark.parametrize(
    "subject,message",
    [
        (EMAIL_SUBJECT, EMAIL_MESSAGE),
        ("", ""),
        (EMAIL_SUBJECT, ""),
        ("", EMAIL_MESSAGE),
    ],
)
def test_contact_admin_page_sends_email(subject, message, admin_client, mailoutbox):
    """Test contact admin messages are emailed if message or subject entered"""
    response: HttpResponse = admin_client.post(
        reverse("common:contact-admin"),
        {
            "subject": subject,
            "message": message,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("dashboard:home")  # type: ignore

    if subject or message:
        assert len(mailoutbox) == 1
        email = mailoutbox[0]
        assert email.subject == subject
        assert email.body == message
        assert email.from_email == "admin@example.com"
        assert email.to == [settings.CONTACT_ADMIN_EMAIL]
    else:
        assert len(mailoutbox) == 0


@pytest.mark.django_db
def test_view_accessibility_statement(client):
    """Test accessibility statement renders. No login required"""
    platform: Platform = get_platform_settings()
    platform.platform_accessibility_statement = "# Accessibility statement header"
    platform.save()

    response: HttpResponse = client.get(reverse("common:accessibility-statement"))

    assert response.status_code == 200
    assertContains(
        response,
        """<h1>Accessibility statement header</h1>""",
        html=True,
    )


@pytest.mark.django_db
def test_view_privacy_notice(client):
    """Test privacy notice renders. No login required."""
    platform: Platform = get_platform_settings()
    platform.platform_privacy_notice = "# Privacy notice header"
    platform.save()

    response: HttpResponse = client.get(reverse("common:privacy-notice"))

    assert response.status_code == 200
    assertContains(
        response,
        """<h1>Privacy notice header</h1>""",
        html=True,
    )


@pytest.mark.parametrize(
    "prototype_name,issue_report_link_expected",
    [
        ("", True),
        ("TEST", True),
        ("anything-else", False),
    ],
)
def test_issue_report_link(prototype_name, issue_report_link_expected, admin_client):
    """
    Test issue report link is rendered on live and test platforms
    but not on prototypes.
    """
    settings.AMP_PROTOTYPE_NAME = prototype_name
    response: HttpResponse = admin_client.get(reverse("dashboard:home"))

    assert response.status_code == 200
    if issue_report_link_expected:
        assertContains(response, ISSUE_REPORT_LINK, html=True)
    else:
        assertNotContains(response, ISSUE_REPORT_LINK, html=True)


@pytest.mark.parametrize(
    "case_field, metric_id, lowercase_label",
    [
        ("created", "cases-created", "cases created"),
        ("testing_details_complete_date", "tests-completed", "tests completed"),
        ("report_sent_date", "reports-sent", "reports sent"),
        ("completed_date", "cases-closed", "cases closed"),
    ],
)
@patch("accessibility_monitoring_platform.apps.common.views.django_timezone")
def test_case_progress_metric_over(
    mock_timezone, case_field, metric_id, lowercase_label, admin_client
):
    """
    Test case progress metric, which is over this month, is calculated and
    displayed correctly.
    """
    mock_timezone.now.return_value = datetime(2022, 1, 10, tzinfo=timezone.utc)

    Case.objects.create(**{case_field: datetime(2021, 11, 5, tzinfo=timezone.utc)})
    Case.objects.create(**{case_field: datetime(2021, 12, 5, tzinfo=timezone.utc)})
    Case.objects.create(**{case_field: datetime(2021, 12, 6, tzinfo=timezone.utc)})
    Case.objects.create(**{case_field: datetime(2022, 1, 1, tzinfo=timezone.utc)})

    response: HttpResponse = admin_client.get(reverse("common:metrics-case"))

    assert response.status_code == 200
    assertContains(
        response,
        CASE_METRIC_OVER_THIS_MONTH.format(
            metric_id=metric_id,
            number_this_month=1,
            percentage_difference=55,
            number_last_month=2,
            lowercase_label=lowercase_label,
        ),
        html=True,
    )


@pytest.mark.parametrize(
    "case_field, metric_id, lowercase_label",
    [
        ("created", "cases-created", "cases created"),
        ("testing_details_complete_date", "tests-completed", "tests completed"),
        ("report_sent_date", "reports-sent", "reports sent"),
        ("completed_date", "cases-closed", "cases closed"),
    ],
)
@patch("accessibility_monitoring_platform.apps.common.views.django_timezone")
def test_case_progress_metric_under(
    mock_timezone, case_field, metric_id, lowercase_label, admin_client
):
    """
    Test case progress metric, which is under this month, is calculated and
    displayed correctly.
    """
    mock_timezone.now.return_value = datetime(2022, 1, 20, tzinfo=timezone.utc)

    Case.objects.create(**{case_field: datetime(2021, 11, 5, tzinfo=timezone.utc)})
    Case.objects.create(**{case_field: datetime(2021, 12, 5, tzinfo=timezone.utc)})
    Case.objects.create(**{case_field: datetime(2021, 12, 6, tzinfo=timezone.utc)})
    Case.objects.create(**{case_field: datetime(2022, 1, 1, tzinfo=timezone.utc)})

    response: HttpResponse = admin_client.get(reverse("common:metrics-case"))

    assert response.status_code == 200
    assertContains(
        response,
        CASE_METRIC_UNDER_THIS_MONTH.format(
            metric_id=metric_id,
            number_this_month=1,
            percentage_difference=23,
            number_last_month=2,
            lowercase_label=lowercase_label,
        ),
        html=True,
    )


@pytest.mark.parametrize(
    "table_id, case_field",
    [
        ("cases-created-over-the-last-year", "created"),
        ("tests-completed-over-the-last-year", "testing_details_complete_date"),
        ("reports-sent-over-the-last-year", "report_sent_date"),
        ("cases-completed-over-the-last-year", "completed_date"),
    ],
)
@patch("accessibility_monitoring_platform.apps.common.views.django_timezone")
def test_case_yearly_metric(mock_timezone, table_id, case_field, admin_client):
    """
    Test case yearly metric table values.
    """
    mock_timezone.now.return_value = datetime(2022, 1, 20, tzinfo=timezone.utc)

    Case.objects.create(**{case_field: datetime(2021, 11, 5, tzinfo=timezone.utc)})
    Case.objects.create(**{case_field: datetime(2021, 12, 5, tzinfo=timezone.utc)})
    Case.objects.create(**{case_field: datetime(2021, 12, 6, tzinfo=timezone.utc)})
    Case.objects.create(**{case_field: datetime(2022, 1, 1, tzinfo=timezone.utc)})

    response: HttpResponse = admin_client.get(reverse("common:metrics-case"))

    assert response.status_code == 200
    assertContains(
        response,
        CASE_METRIC_YEARLY_TABLE.format(table_id=table_id),
        html=True,
    )


@patch("accessibility_monitoring_platform.apps.common.views.django_timezone")
def test_progress_policy_metric_website_compliance(mock_timezone, admin_client):
    """
    Test case yearly metric table values.
    """
    mock_timezone.now.return_value = datetime(2022, 1, 20, tzinfo=timezone.utc)

    case: Case = Case.objects.create(case_completed="complete-no-send")
    Audit.objects.create(
        case=case, retest_date=datetime(2021, 12, 15, tzinfo=timezone.utc)
    )
    fixed_case: Case = Case.objects.create(
        case_completed="complete-no-send",
        recommendation_for_enforcement=RECOMMENDATION_NO_ACTION,
    )
    Audit.objects.create(
        case=fixed_case, retest_date=datetime(2021, 12, 5, tzinfo=timezone.utc)
    )

    response: HttpResponse = admin_client.get(reverse("common:metrics-policy"))

    assert response.status_code == 200
    assertContains(
        response,
        POLICY_PROGRESS_METRIC.format(
            id="websites-compliant-after-retest-in-the-last-90-days",
            percentage=50,
            partial_count=1,
            total_count=2,
        ),
        html=True,
    )
