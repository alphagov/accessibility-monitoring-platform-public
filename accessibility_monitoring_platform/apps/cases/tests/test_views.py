"""
Tests for cases views
"""
from datetime import date, datetime, timedelta
import pytest
import pytz
from typing import List

from pytest_django.asserts import assertContains, assertNotContains

from django.contrib.auth.models import User, Group
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.urls import reverse
from django.utils.text import slugify

from ..models import Case, Contact
from ..views import (
    ONE_WEEK_IN_DAYS,
    FOUR_WEEKS_IN_DAYS,
    TWELVE_WEEKS_IN_DAYS,
    find_duplicate_cases,
    calculate_report_followup_dates,
    calculate_twelve_week_chaser_dates,
    format_due_date_help_text,
)
from ...common.models import Sector
from ...common.utils import format_date, get_field_names_for_export

CONTACT_EMAIL: str = "test@email.com"
DOMAIN: str = "domain.com"
HOME_PAGE_URL: str = f"https://{DOMAIN}"
ORGANISATION_NAME: str = "Organisation name"
REPORT_SENT_DATE: date = date(2021, 2, 28)
OTHER_DATE: date = date(2020, 12, 31)
ONE_WEEK_FOLLOWUP_DUE_DATE: date = REPORT_SENT_DATE + timedelta(days=ONE_WEEK_IN_DAYS)
FOUR_WEEK_FOLLOWUP_DUE_DATE: date = REPORT_SENT_DATE + timedelta(
    days=FOUR_WEEKS_IN_DAYS
)
TWELVE_WEEK_FOLLOWUP_DUE_DATE: date = REPORT_SENT_DATE + timedelta(
    days=TWELVE_WEEKS_IN_DAYS
)
TODAY: date = date.today()
case_fields_to_export_str = ",".join(get_field_names_for_export(Case))


def add_user_to_auditor_groups(user: User) -> None:
    auditor_group: Group = Group.objects.create(name="Auditor")
    qa_auditor_group: Group = Group.objects.create(name="QA auditor")
    auditor_group.user_set.add(user)
    qa_auditor_group.user_set.add(user)


def test_case_detail_view_leaves_out_deleted_contact(admin_client):
    """Test that deleted Contacts are not included in context"""
    case: Case = Case.objects.create()
    undeleted_contact: Contact = Contact.objects.create(
        case=case,
        first_name="Undeleted",
        last_name="Contact",
    )
    Contact.objects.create(
        case=case,
        first_name="Deleted",
        last_name="Contact",
        is_deleted=True,
    )

    response: HttpResponse = admin_client.get(
        reverse("cases:case-detail", kwargs={"pk": case.id})
    )

    assert response.status_code == 200
    assert set(response.context["contacts"]) == set([undeleted_contact])
    assertContains(response, "Undeleted Contact")
    assertNotContains(response, "Deleted Contact")


def test_case_list_view_leaves_out_deleted_case(admin_client):
    """Test that the case list view page does not include deleted cases"""
    Case.objects.create(organisation_name="Not Deleted")
    Case.objects.create(organisation_name="Is Deleted", is_deleted=True)

    response: HttpResponse = admin_client.get(reverse("cases:case-list"))

    assert response.status_code == 200
    assertContains(response, '<h2 class="govuk-heading-m">1 cases found</h2>')
    assertContains(response, "Not Deleted")
    assertNotContains(response, "Is Deleted")


def test_case_list_view_filtering_by_deleted_includes_deleted_contact(admin_client):
    """Test that deleted Cases are included in context when filtering by status 'deleted'"""
    Case.objects.create(organisation_name="Not Deleted")
    Case.objects.create(organisation_name="Is Deleted", is_deleted=True)

    response: HttpResponse = admin_client.get(
        f'{reverse("cases:case-list")}?status=deleted'
    )

    assert response.status_code == 200
    assertContains(response, '<h2 class="govuk-heading-m">1 cases found</h2>')
    assertContains(response, "Is Deleted")
    assertNotContains(response, "Not Deleted")


def test_case_list_view_filters_by_unassigned_qa_case(admin_client):
    """Test that Cases where Report is ready to QA can be filtered by status"""
    Case.objects.create(organisation_name="Excluded")
    Case.objects.create(
        organisation_name="Included", report_review_status="ready-to-review"
    )

    response: HttpResponse = admin_client.get(
        f'{reverse("cases:case-list")}?status=unassigned-qa-case'
    )

    assert response.status_code == 200
    assertContains(response, '<h2 class="govuk-heading-m">1 cases found</h2>')
    assertContains(response, "Included")
    assertNotContains(response, "Excluded")


def test_case_list_view_filters_by_case_number(admin_client):
    """Test that the case list view page can be filtered by case number"""
    included_case: Case = Case.objects.create(organisation_name="Included")
    Case.objects.create(organisation_name="Excluded")

    response: HttpResponse = admin_client.get(
        f"{reverse('cases:case-list')}?search={included_case.id}"
    )

    assert response.status_code == 200
    assertContains(response, '<h2 class="govuk-heading-m">1 cases found</h2>')
    assertContains(response, "Included")
    assertNotContains(response, "Excluded")


def test_case_list_view_filters_by_psb_location(admin_client):
    """Test that the case list view page can be filtered by case number"""
    Case.objects.create(organisation_name="Included", psb_location="scotland")
    Case.objects.create(organisation_name="Excluded")

    response: HttpResponse = admin_client.get(
        f"{reverse('cases:case-list')}?search=scot"
    )

    assert response.status_code == 200
    assertContains(response, '<h2 class="govuk-heading-m">1 cases found</h2>')
    assertContains(response, "Included")
    assertNotContains(response, "Excluded")


def test_case_list_view_filters_by_sector(admin_client):
    """Test that the case list view page can be filtered by case number"""
    sector: Sector = Sector.objects.create(name="Defence")
    Case.objects.create(organisation_name="Included", sector=sector)
    Case.objects.create(organisation_name="Excluded")

    response: HttpResponse = admin_client.get(
        f"{reverse('cases:case-list')}?search=fence"
    )

    assert response.status_code == 200
    assertContains(response, '<h2 class="govuk-heading-m">1 cases found</h2>')
    assertContains(response, "Included")
    assertNotContains(response, "Excluded")


@pytest.mark.parametrize(
    "field_name,value,url_parameter_name",
    [
        ("home_page_url", "included.com", "search"),
        ("organisation_name", "IncludedOrg", "search"),
    ],
)
def test_case_list_view_string_filters(
    field_name, value, url_parameter_name, admin_client
):
    """Test that the case list view page can be filtered by string"""
    included_case: Case = Case.objects.create(organisation_name="Included")
    setattr(included_case, field_name, value)
    included_case.save()

    Case.objects.create(organisation_name="Excluded")

    response: HttpResponse = admin_client.get(
        f"{reverse('cases:case-list')}?{url_parameter_name}={value}"
    )

    assert response.status_code == 200
    assertContains(response, '<h2 class="govuk-heading-m">1 cases found</h2>')
    assertContains(response, "Included")
    assertNotContains(response, "Excluded")


@pytest.mark.parametrize(
    "field_name,url_parameter_name",
    [
        ("auditor", "auditor"),
        ("reviewer", "reviewer"),
    ],
)
def test_case_list_view_user_filters(field_name, url_parameter_name, admin_client):
    """Test that the case list view page can be filtered by user"""
    user: User = User.objects.create()
    add_user_to_auditor_groups(user)

    included_case: Case = Case.objects.create(organisation_name="Included")
    setattr(included_case, field_name, user)
    included_case.save()

    Case.objects.create(organisation_name="Excluded")

    response: HttpResponse = admin_client.get(
        f"{reverse('cases:case-list')}?{url_parameter_name}={user.id}"
    )

    assert response.status_code == 200
    assertContains(response, '<h2 class="govuk-heading-m">1 cases found</h2>')
    assertContains(response, "Included")
    assertNotContains(response, "Excluded")


@pytest.mark.parametrize(
    "field_name,url_parameter_name",
    [
        ("auditor", "auditor"),
        ("reviewer", "reviewer"),
    ],
)
def test_case_list_view_user_unassigned_filters(
    field_name, url_parameter_name, admin_client
):
    """Test that the case list view page can be filtered by unassigned user values"""
    Case.objects.create(organisation_name="Included")

    user = User.objects.create()
    excluded_case: Case = Case.objects.create(organisation_name="Excluded")
    setattr(excluded_case, field_name, user)
    excluded_case.save()

    response: HttpResponse = admin_client.get(
        f"{reverse('cases:case-list')}?{url_parameter_name}=none"
    )

    assert response.status_code == 200
    assertContains(response, '<h2 class="govuk-heading-m">1 cases found</h2>')
    assertContains(response, "Included")
    assertNotContains(response, "Excluded")


def test_case_list_view_date_range_filters(admin_client):
    """Test that the case list view page can be filtered by date range"""
    included_created_date: datetime = datetime(
        year=2021, month=6, day=5, tzinfo=pytz.UTC
    )
    excluded_created_date: datetime = datetime(
        year=2021, month=5, day=5, tzinfo=pytz.UTC
    )
    Case.objects.create(organisation_name="Included", created=included_created_date)
    Case.objects.create(organisation_name="Excluded", created=excluded_created_date)

    url_parameters = "start_date_0=1&start_date_1=6&start_date_2=2021&end_date_0=10&end_date_1=6&end_date_2=2021"
    response: HttpResponse = admin_client.get(
        f"{reverse('cases:case-list')}?{url_parameters}"
    )

    assert response.status_code == 200
    assertContains(response, '<h2 class="govuk-heading-m">1 cases found</h2>')
    assertContains(response, "Included")
    assertNotContains(response, "Excluded")


def test_case_export_list_view(admin_client):
    """Test that the case export list view returns csv data"""
    response: HttpResponse = admin_client.get(reverse("cases:case-export-list"))

    assert response.status_code == 200
    assertContains(response, case_fields_to_export_str)


def test_case_export_list_view_respects_filters(admin_client):
    """Test that the case export list view includes only filtered data"""
    user: User = User.objects.create()
    add_user_to_auditor_groups(user)
    Case.objects.create(organisation_name="Included", auditor=user)
    Case.objects.create(organisation_name="Excluded")

    response: HttpResponse = admin_client.get(
        f"{reverse('cases:case-export-list')}?auditor={user.id}"
    )

    assert response.status_code == 200
    assertContains(response, "Included")
    assertNotContains(response, "Excluded")


def test_case_export_single_view(admin_client):
    """Test that the case export single view returns csv data"""
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.get(
        reverse("cases:case-export-single", kwargs={"pk": case.id})
    )

    assert response.status_code == 200
    assertContains(response, case_fields_to_export_str)


def test_delete_case_view(admin_client):
    """Test that delete case view deletes case"""
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.post(
        reverse("cases:delete-case", kwargs={"pk": case.id})
    )

    assert response.status_code == 302
    assert response.url == reverse("cases:case-list")

    case_from_db: Case = Case.objects.get(pk=case.id)

    assert case_from_db.is_deleted


def test_restore_case_view(admin_client):
    """Test that restore case view restores case"""
    case: Case = Case.objects.create(is_deleted=True)

    response: HttpResponse = admin_client.post(
        reverse("cases:restore-case", kwargs={"pk": case.id})
    )

    assert response.status_code == 302
    assert response.url == reverse("cases:case-detail", kwargs={"pk": case.id})

    case_from_db: Case = Case.objects.get(pk=case.id)

    assert case_from_db.is_deleted is False


@pytest.mark.parametrize(
    "path_name, expected_content",
    [
        ("cases:case-list", '<h1 class="govuk-heading-xl">Search</h1>'),
        ("cases:case-create", '<h1 class="govuk-heading-xl">Create case</h1>'),
    ],
)
def test_non_case_specific_page_loads(path_name, expected_content, admin_client):
    """Test that the non-case-specific view page loads"""
    response: HttpResponse = admin_client.get(reverse(path_name))

    assert response.status_code == 200
    assertContains(response, expected_content)


@pytest.mark.parametrize(
    "path_name, expected_content",
    [
        (
            "cases:case-detail",
            '<h1 class="govuk-heading-xl" style="margin-bottom:15px; padding-right: 20px;">View case</h1>',
        ),
        ("cases:edit-case-details", "<li>Case details</li>"),
        ("cases:edit-test-results", "<li>Testing details</li>"),
        ("cases:edit-report-details", "<li>Report details</li>"),
        ("cases:edit-contact-details", "<li>Contact details</li>"),
        ("cases:edit-report-correspondence", "<li>Report correspondence</li>"),
    ],
)
def test_case_specific_page_loads(path_name, expected_content, admin_client):
    """Test that the case-specific view page loads"""
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.get(
        reverse(path_name, kwargs={"pk": case.id})
    )

    assert response.status_code == 200

    assertContains(response, expected_content, html=True)


def test_create_case_shows_error_messages(admin_client):
    """
    Test that the create case page shows the expected error messages
    """
    response: HttpResponse = admin_client.post(
        reverse("cases:case-create"),
        {
            "home_page_url": "gov.uk",
            "save_exit": "Save and exit",
        },
    )

    assert response.status_code == 200
    assertContains(
        response,
        """<p class="govuk-error-message">
            <span class="govuk-visually-hidden">Error:</span>
            URL must start with http:// or https://
        </p>""",
        html=True,
    )
    assertContains(
        response,
        """<p class="govuk-error-message">
            <span class="govuk-visually-hidden">Error:</span>
            Choose which equalities body will check the case
        </p>""",
        html=True,
    )


@pytest.mark.parametrize(
    "button_name, expected_redirect_url",
    [
        ("save_continue_case", reverse("cases:edit-case-details", kwargs={"pk": 1})),
        ("save_new_case", reverse("cases:case-create")),
        ("save_exit", reverse("cases:case-list")),
    ],
)
def test_create_case_redirects_based_on_button_pressed(
    button_name, expected_redirect_url, admin_client
):
    """Test that a successful case create redirects based on the button pressed"""
    response: HttpResponse = admin_client.post(
        reverse("cases:case-create"),
        {
            "home_page_url": HOME_PAGE_URL,
            "enforcement_body": "ehrc",
            button_name: "Button value",
        },
    )

    assert response.status_code == 302
    assert response.url == expected_redirect_url


@pytest.mark.django_db
def test_create_case_shows_duplicate_cases(admin_client):
    """Test that create case shows duplicates found"""
    other_url: str = "other_url"
    other_organisation_name: str = "other organisation name"
    Case.objects.create(
        home_page_url=HOME_PAGE_URL,
        organisation_name=other_organisation_name,
    )
    Case.objects.create(
        organisation_name=ORGANISATION_NAME,
        home_page_url=other_url,
    )

    response: HttpResponse = admin_client.post(
        reverse("cases:case-create"),
        {
            "home_page_url": HOME_PAGE_URL,
            "enforcement_body": "ehrc",
            "organisation_name": ORGANISATION_NAME,
        },
    )

    assert response.status_code == 200
    assertContains(response, other_url)
    assertContains(response, other_organisation_name)


@pytest.mark.parametrize(
    "button_name, expected_redirect_url",
    [
        ("save_continue_case", reverse("cases:edit-case-details", kwargs={"pk": 3})),
        ("save_new_case", reverse("cases:case-create")),
        ("save_exit", reverse("cases:case-list")),
    ],
)
@pytest.mark.django_db
def test_create_case_can_create_duplicate_cases(
    button_name, expected_redirect_url, admin_client
):
    """Test that create case can create duplicate cases"""
    Case.objects.create(home_page_url=HOME_PAGE_URL)
    Case.objects.create(organisation_name=ORGANISATION_NAME)

    response: HttpResponse = admin_client.post(
        f"{reverse('cases:case-create')}?allow_duplicate_cases=True",
        {
            "home_page_url": HOME_PAGE_URL,
            "enforcement_body": "ehrc",
            "organisation_name": ORGANISATION_NAME,
            button_name: "Button value",
        },
    )

    assert response.status_code == 302
    assert response.url == expected_redirect_url


@pytest.mark.parametrize(
    "case_edit_path, button_name, expected_redirect_path, expected_page_anchor",
    [
        ("cases:edit-case-details", "save_continue", "cases:edit-test-results", ""),
        ("cases:edit-case-details", "save_exit", "cases:case-detail", "#case-details"),
        ("cases:edit-test-results", "save_continue", "cases:edit-report-details", ""),
        (
            "cases:edit-test-results",
            "save_exit",
            "cases:case-detail",
            "#testing-details",
        ),
        (
            "cases:edit-report-details",
            "save_continue",
            "cases:edit-contact-details",
            "",
        ),
        (
            "cases:edit-report-details",
            "save_exit",
            "cases:case-detail",
            "#report-details",
        ),
        (
            "cases:edit-contact-details",
            "save_continue",
            "cases:edit-report-correspondence",
            "",
        ),
        (
            "cases:edit-contact-details",
            "save_exit",
            "cases:case-detail",
            "#contact-details",
        ),
        (
            "cases:edit-report-correspondence",
            "save_exit",
            "cases:case-detail",
            "#report-correspondence",
        ),
        (
            "cases:edit-report-correspondence",
            "save_continue",
            "cases:edit-twelve-week-correspondence",
            "",
        ),
        (
            "cases:edit-report-followup-due-dates",
            "save_return",
            "cases:edit-report-correspondence",
            "",
        ),
        (
            "cases:edit-twelve-week-correspondence",
            "save_exit",
            "cases:case-detail",
            "#12-week-correspondence",
        ),
        (
            "cases:edit-twelve-week-correspondence",
            "save_continue",
            "cases:edit-final-decision",
            "",
        ),
        (
            "cases:edit-twelve-week-correspondence-due-dates",
            "save_return",
            "cases:edit-twelve-week-correspondence",
            "",
        ),
        (
            "cases:edit-no-psb-response",
            "save_continue",
            "cases:edit-enforcement-body-correspondence",
            "",
        ),
        (
            "cases:edit-final-decision",
            "save_exit",
            "cases:case-detail",
            "#final-decision",
        ),
        (
            "cases:edit-final-decision",
            "save_continue",
            "cases:edit-enforcement-body-correspondence",
            "",
        ),
        (
            "cases:edit-enforcement-body-correspondence",
            "save_exit",
            "cases:case-detail",
            "#equality-body-correspondence",
        ),
    ],
)
def test_case_edit_redirects_based_on_button_pressed(
    case_edit_path,
    button_name,
    expected_redirect_path,
    expected_page_anchor,
    admin_client,
):
    """Test that a successful case update redirects based on the button pressed"""
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.post(
        reverse(case_edit_path, kwargs={"pk": case.id}),
        {
            "home_page_url": HOME_PAGE_URL,
            "enforcement_body": "ehrc",
            button_name: "Button value",
        },
    )
    assert response.status_code == 302
    assert (
        response.url
        == f'{reverse(expected_redirect_path, kwargs={"pk": case.id})}{expected_page_anchor}'
    )


def test_add_contact_form_appears(admin_client):
    """Test that pressing the add contact button adds a new contact form"""
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.post(
        reverse("cases:edit-contact-details", kwargs={"pk": case.id}),
        {
            "add_contact": "Button value",
        },
        follow=True,
    )
    assert response.status_code == 200
    assertContains(response, "Contact 1")


def test_add_contact(admin_client):
    """Test adding a contact"""
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.post(
        reverse("cases:edit-contact-details", kwargs={"pk": case.id}),
        {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": "",
            "form-0-first_name": "",
            "form-0-last_name": "",
            "form-0-job_title": "",
            "form-0-email": CONTACT_EMAIL,
            "form-0-notes": "",
            "save_continue": "Save and continue",
        },
        follow=True,
    )
    assert response.status_code == 200

    contacts: QuerySet[Contact] = Contact.objects.filter(case=case)
    assert contacts.count() == 1
    assert list(contacts)[0].email == CONTACT_EMAIL


def test_delete_contact(admin_client):
    """Test that pressing the remove contact button deletes the contact"""
    case: Case = Case.objects.create()
    contact: Contact = Contact.objects.create(case=case)

    response: HttpResponse = admin_client.post(
        reverse("cases:edit-contact-details", kwargs={"pk": case.id}),
        {
            f"remove_contact_{contact.id}": "Button value",
        },
        follow=True,
    )
    assert response.status_code == 200
    assertContains(response, "No contacts have been entered")

    contact_on_database = Contact.objects.get(pk=contact.id)
    assert contact_on_database.is_deleted is True


def test_preferred_contact_not_displayed_on_form(admin_client):
    """
    Test that the preferred contact field is not displayed when there is only one contact
    """
    case: Case = Case.objects.create()
    Contact.objects.create(case=case)

    response: HttpResponse = admin_client.get(
        reverse("cases:edit-contact-details", kwargs={"pk": case.id}),
    )
    assert response.status_code == 200
    assertNotContains(response, "Preferred contact?")


def test_preferred_contact_displayed_on_form(admin_client):
    """
    Test that the preferred contact field is displayed when there is more than one contact
    """
    case: Case = Case.objects.create()
    Contact.objects.create(case=case)
    Contact.objects.create(case=case)

    response: HttpResponse = admin_client.get(
        reverse("cases:edit-contact-details", kwargs={"pk": case.id}),
    )
    assert response.status_code == 200
    assertContains(response, "Preferred contact?")


def test_updating_report_sent_date(admin_client):
    """Test that populating the report sent date populates the report followup due dates"""
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.post(
        reverse("cases:edit-report-correspondence", kwargs={"pk": case.id}),
        {
            "report_sent_date_0": REPORT_SENT_DATE.day,
            "report_sent_date_1": REPORT_SENT_DATE.month,
            "report_sent_date_2": REPORT_SENT_DATE.year,
            "save_continue": "Button value",
        },
    )
    assert response.status_code == 302

    case_from_db: Case = Case.objects.get(pk=case.id)

    assert case_from_db.report_followup_week_1_due_date == ONE_WEEK_FOLLOWUP_DUE_DATE
    assert case_from_db.report_followup_week_4_due_date == FOUR_WEEK_FOLLOWUP_DUE_DATE
    assert (
        case_from_db.report_followup_week_12_due_date == TWELVE_WEEK_FOLLOWUP_DUE_DATE
    )


def test_report_followup_due_dates_not_changed(admin_client):
    """
    Test that populating the report sent date does not update existing report followup due dates
    """
    case: Case = Case.objects.create(
        report_followup_week_1_due_date=OTHER_DATE,
        report_followup_week_4_due_date=OTHER_DATE,
        report_followup_week_12_due_date=OTHER_DATE,
    )

    response: HttpResponse = admin_client.post(
        reverse("cases:edit-report-details", kwargs={"pk": case.id}),
        {
            "report_sent_date_0": REPORT_SENT_DATE.day,
            "report_sent_date_1": REPORT_SENT_DATE.month,
            "report_sent_date_2": REPORT_SENT_DATE.year,
            "save_continue": "Button value",
        },
    )
    assert response.status_code == 302

    case_from_db: Case = Case.objects.get(pk=case.id)

    assert case_from_db.report_followup_week_1_due_date == OTHER_DATE
    assert case_from_db.report_followup_week_4_due_date == OTHER_DATE
    assert case_from_db.report_followup_week_12_due_date == OTHER_DATE


def test_report_followup_due_dates_not_changed_if_repot_sent_date_already_set(
    admin_client,
):
    """
    Test that updating the report sent date does not populate report followup due dates
    """
    case: Case = Case.objects.create(report_sent_date=OTHER_DATE)

    response: HttpResponse = admin_client.post(
        reverse("cases:edit-report-details", kwargs={"pk": case.id}),
        {
            "report_sent_date_0": REPORT_SENT_DATE.day,
            "report_sent_date_1": REPORT_SENT_DATE.month,
            "report_sent_date_2": REPORT_SENT_DATE.year,
            "save_continue": "Button value",
        },
    )
    assert response.status_code == 302

    case_from_db: Case = Case.objects.get(pk=case.id)

    assert case_from_db.report_followup_week_1_due_date is None
    assert case_from_db.report_followup_week_4_due_date is None
    assert case_from_db.report_followup_week_12_due_date is None


def test_case_report_correspondence_view_contains_followup_due_dates(admin_client):
    """Test that the case report correspondence view contains the followup due dates"""
    case: Case = Case.objects.create(
        report_followup_week_1_due_date=ONE_WEEK_FOLLOWUP_DUE_DATE,
        report_followup_week_4_due_date=FOUR_WEEK_FOLLOWUP_DUE_DATE,
        report_followup_week_12_due_date=TWELVE_WEEK_FOLLOWUP_DUE_DATE,
    )

    response: HttpResponse = admin_client.get(
        reverse("cases:edit-report-correspondence", kwargs={"pk": case.id})
    )

    assert response.status_code == 200
    assertContains(
        response,
        f'<div class="govuk-hint">Due {format_date(ONE_WEEK_FOLLOWUP_DUE_DATE)}</div>',
    )
    assertContains(
        response,
        f'<div class="govuk-hint">Due {format_date(FOUR_WEEK_FOLLOWUP_DUE_DATE)}</div>',
    )
    assertContains(
        response,
        f'<div class="govuk-hint">Due {format_date(TWELVE_WEEK_FOLLOWUP_DUE_DATE)}</div>',
        html=True,
    )


def test_setting_report_followup_populates_sent_dates(admin_client):
    """Test that ticking the report followup checkboxes populates the report followup sent dates"""
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.post(
        reverse("cases:edit-report-correspondence", kwargs={"pk": case.id}),
        {
            "report_followup_week_1_sent_date": "on",
            "report_followup_week_4_sent_date": "on",
            "save_continue": "Button value",
        },
    )
    assert response.status_code == 302

    case_from_db: Case = Case.objects.get(pk=case.id)

    assert case_from_db.report_followup_week_1_sent_date == TODAY
    assert case_from_db.report_followup_week_4_sent_date == TODAY


def test_setting_report_followup_doesn_not_update_sent_dates(admin_client):
    """Test that ticking the report followup checkboxes does not update the report followup sent dates"""
    case: Case = Case.objects.create(
        report_followup_week_1_sent_date=OTHER_DATE,
        report_followup_week_4_sent_date=OTHER_DATE,
    )

    response: HttpResponse = admin_client.post(
        reverse("cases:edit-report-correspondence", kwargs={"pk": case.id}),
        {
            "report_followup_week_1_sent_date": "on",
            "report_followup_week_4_sent_date": "on",
            "save_continue": "Button value",
        },
    )
    assert response.status_code == 302

    case_from_db: Case = Case.objects.get(pk=case.id)

    assert case_from_db.report_followup_week_1_sent_date == OTHER_DATE
    assert case_from_db.report_followup_week_4_sent_date == OTHER_DATE


def test_unsetting_report_followup_sent_dates(admin_client):
    """Test that not ticking the report followup checkboxes clears the report followup sent dates"""
    case: Case = Case.objects.create(
        report_followup_week_1_sent_date=OTHER_DATE,
        report_followup_week_4_sent_date=OTHER_DATE,
    )

    response: HttpResponse = admin_client.post(
        reverse("cases:edit-report-correspondence", kwargs={"pk": case.id}),
        {
            "save_continue": "Button value",
        },
    )
    assert response.status_code == 302

    case_from_db: Case = Case.objects.get(pk=case.id)

    assert case_from_db.report_followup_week_1_sent_date is None
    assert case_from_db.report_followup_week_4_sent_date is None


@pytest.mark.parametrize(
    "url, domain, expected_number_of_duplicates",
    [
        (HOME_PAGE_URL, ORGANISATION_NAME, 2),
        (HOME_PAGE_URL, "", 1),
        ("https://domain2.com", "Org name", 0),
        ("https://domain2.com", "", 0),
    ],
)
@pytest.mark.django_db
def test_find_duplicate_cases(url, domain, expected_number_of_duplicates):
    """Test find_duplicate_cases returns matching cases"""
    organisation_name_case: Case = Case.objects.create(
        organisation_name=ORGANISATION_NAME
    )
    domain_case: Case = Case.objects.create(home_page_url=HOME_PAGE_URL)

    duplicate_cases: List[Case] = list(find_duplicate_cases(url, domain))

    assert len(duplicate_cases) == expected_number_of_duplicates

    if expected_number_of_duplicates > 0:
        assert duplicate_cases[0] == domain_case

    if expected_number_of_duplicates > 1:
        assert duplicate_cases[1] == organisation_name_case


def test_preferred_contact_not_displayed(admin_client):
    """
    Test that the preferred contact is not displayed when there is only one contact
    """
    case: Case = Case.objects.create()
    Contact.objects.create(case=case)

    response: HttpResponse = admin_client.get(
        reverse("cases:case-detail", kwargs={"pk": case.id}),
    )
    assert response.status_code == 200
    assertNotContains(response, "Preferred contact")


def test_preferred_contact_displayed(admin_client):
    """
    Test that the preferred contact is displayed when there is more than one contact
    """
    case: Case = Case.objects.create()
    Contact.objects.create(case=case)
    Contact.objects.create(case=case)

    response: HttpResponse = admin_client.get(
        reverse("cases:case-detail", kwargs={"pk": case.id}),
    )
    assert response.status_code == 200
    assertContains(response, "Preferred contact")


@pytest.mark.parametrize(
    "flag_name, section_name, edit_url_name",
    [
        ("case_details_complete_date", "Case details", "edit-case-details"),
        ("contact_details_complete_date", "Contact details", "edit-contact-details"),
        ("testing_details_complete_date", "Testing details", "edit-test-results"),
        ("reporting_details_complete_date", "Report details", "edit-report-details"),
        (
            "report_correspondence_complete_date",
            "Report correspondence",
            "edit-report-correspondence",
        ),
        (
            "twelve_week_correspondence_complete_date",
            "12 week correspondence",
            "edit-twelve-week-correspondence",
        ),
        ("final_decision_complete_date", "Final decision", "edit-final-decision"),
        (
            "enforcement_correspondence_complete_date",
            "Equality body correspondence",
            "edit-enforcement-body-correspondence",
        ),
    ],
)
def test_section_complete_check_displayed_in_contents(
    flag_name, section_name, edit_url_name, admin_client
):
    """
    Test that the section complete tick is displayed in contents
    """
    case: Case = Case.objects.create()
    setattr(case, flag_name, TODAY)
    case.save()
    edit_url: str = reverse(f"cases:{edit_url_name}", kwargs={"pk": case.id})

    response: HttpResponse = admin_client.get(
        reverse("cases:case-detail", kwargs={"pk": case.id}),
    )

    assert response.status_code == 200

    assertContains(
        response,
        f"""<li>
            <a href="#{slugify(section_name)}" class="govuk-link govuk-link--no-visited-state">
            {section_name}<span class="govuk-visually-hidden">complete</span></a>
            |
            <a href="{edit_url}" class="govuk-link govuk-link--no-visited-state">
                Edit<span class="govuk-visually-hidden">complete</span>
            </a>
            &check;
        </li>""",
        html=True,
    )


@pytest.mark.parametrize(
    "step_url, flag_name, step_name",
    [
        ("cases:edit-case-details", "case_details_complete_date", "Case details"),
        ("cases:edit-test-results", "testing_details_complete_date", "Testing details"),
        (
            "cases:edit-report-details",
            "reporting_details_complete_date",
            "Report details",
        ),
        (
            "cases:edit-contact-details",
            "contact_details_complete_date",
            "Contact details",
        ),
        (
            "cases:edit-report-correspondence",
            "report_correspondence_complete_date",
            "Report correspondence",
        ),
        (
            "cases:edit-twelve-week-correspondence",
            "twelve_week_correspondence_complete_date",
            "12 week correspondence",
        ),
        ("cases:edit-final-decision", "final_decision_complete_date", "Final decision"),
        (
            "cases:edit-enforcement-body-correspondence",
            "enforcement_correspondence_complete_date",
            "Equality body correspondence",
        ),
    ],
)
def test_section_complete_check_displayed_in_steps(
    step_url, flag_name, step_name, admin_client
):
    """
    Test that the section complete tick is displayed in list of steps
    """
    case: Case = Case.objects.create()
    setattr(case, flag_name, TODAY)
    case.save()

    response: HttpResponse = admin_client.get(
        reverse(step_url, kwargs={"pk": case.id}),
    )

    assert response.status_code == 200

    assertContains(
        response,
        f'{step_name}<span class="govuk-visually-hidden">complete</span> &check;',
        html=True,
    )


def test_case_final_decision_view_contains_link_to_test_results_url(admin_client):
    """Test that the case final decision view contains the link to the test results"""
    test_results_url: str = "https://test-results-url"
    case: Case = Case.objects.create(test_results_url=test_results_url)

    response: HttpResponse = admin_client.get(
        reverse("cases:edit-final-decision", kwargs={"pk": case.id})
    )

    assert response.status_code == 200
    assertContains(
        response,
        '<div class="govuk-hint">'
        f'The retest form can be found in the <a href="{test_results_url}"'
        ' class="govuk-link govuk-link--no-visited-state" target="_blank">test results</a>'
        "</div>",
    )


def test_case_final_decision_view_contains_no_link_to_test_results_url(admin_client):
    """Test that the case final decision view contains no link to the test results if none is on case"""
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.get(
        reverse("cases:edit-final-decision", kwargs={"pk": case.id})
    )

    assert response.status_code == 200
    assertContains(
        response,
        '<div class="govuk-hint">'
        "There is no test spreadsheet for this case"
        "</div>",
    )


def test_case_final_decision_view_contains_placeholder_no_accessibility_statement_notes(
    admin_client,
):
    """
    Test that the case final decision view contains placeholder text if there are no accessibility statement notes
    """
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.get(
        reverse("cases:edit-final-decision", kwargs={"pk": case.id})
    )

    assert response.status_code == 200
    assertContains(
        response,
        """<div class="govuk-form-group">
            <label class="govuk-label"><b>Initial accessibility statement notes</b></label>
            <div class="govuk-hint">
                No notes for this case
            </div>
        </div>""",
        html=True,
    )


def test_case_final_decision_view_contains_placeholder_no_compliance_decision_notes(
    admin_client,
):
    """
    Test that the case final decision view contains placeholder text if there are no compliance decision notes
    """
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.get(
        reverse("cases:edit-final-decision", kwargs={"pk": case.id})
    )

    assert response.status_code == 200
    assertContains(
        response,
        """<div class="govuk-form-group">
            <label class="govuk-label"><b>Initial compliance notes</b></label>
            <div class="govuk-hint">
                No notes for this case
            </div>
        </div>""",
        html=True,
    )


def test_calculate_report_followup_dates():
    """
    Test that the report followup dates are calculated correctly.
    """
    case: Case = Case()
    report_sent_date: date = date(2020, 1, 1)

    updated_case = calculate_report_followup_dates(
        case=case, report_sent_date=report_sent_date
    )

    assert updated_case.report_followup_week_1_due_date == date(2020, 1, 8)
    assert updated_case.report_followup_week_4_due_date == date(2020, 1, 29)
    assert updated_case.report_followup_week_12_due_date == date(2020, 3, 25)


def test_calculate_twelve_week_chaser_dates():
    """
    Test that the twelve week chaser dates are calculated correctly.
    """
    case: Case = Case()
    twelve_week_update_requested_date: date = date(2020, 1, 1)

    updated_case = calculate_twelve_week_chaser_dates(
        case=case, twelve_week_update_requested_date=twelve_week_update_requested_date
    )

    assert updated_case.twelve_week_1_week_chaser_due_date == date(2020, 1, 8)
    assert updated_case.twelve_week_4_week_chaser_due_date == date(2020, 1, 29)


@pytest.mark.parametrize(
    "due_date, expected_help_text",
    [
        (date(2020, 1, 1), "Due 01/01/2020"),
        (None, "None"),
    ],
)
def test_format_due_date_help_text(due_date, expected_help_text):
    """
    Test due date formatting for help text
    """
    assert format_due_date_help_text(due_date) == expected_help_text


def test_case_details_includes_link_to_auditors_cases(admin_client):
    """
    Test that the case details page contains a link to all the auditor's cases
    """
    user: User = User.objects.create(first_name="Joe", last_name="Bloggs")
    case: Case = Case.objects.create(auditor=user)

    response: HttpResponse = admin_client.get(
        reverse("cases:case-detail", kwargs={"pk": case.id}),
    )
    assert response.status_code == 200
    assertContains(
        response,
        f"""<tr class="govuk-table__row">
            <th scope="row" class="govuk-table__header amp-width-one-half">Auditor</th>
            <td class="govuk-table__cell amp-width-one-half">
                <a href="{reverse("cases:case-list")}?auditor={ user.id }" rel="noreferrer noopener" class="govuk-link">
                    Joe Bloggs
                </a>
            </td>
        </tr>""",
        html=True,
    )


def test_case_details_has_no_link_to_auditors_cases_if_no_auditor(admin_client):
    """
    Test that the case details page contains no link to the auditor's cases if no auditor is set
    """
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.get(
        reverse("cases:case-detail", kwargs={"pk": case.id}),
    )
    assert response.status_code == 200
    assertContains(
        response,
        """<tr class="govuk-table__row">
            <th scope="row" class="govuk-table__header amp-width-one-half">Auditor</th>
            <td class="govuk-table__cell amp-width-one-half">None</td>
        </tr>""",
        html=True,
    )


def test_case_details_includes_link_to_report(admin_client):
    """
    Test that the case details page contains a link to the report
    """
    report_final_pdf_url: str = "https://report-final-pdf-url.com"
    case: Case = Case.objects.create(report_final_pdf_url=report_final_pdf_url)

    response: HttpResponse = admin_client.get(
        reverse("cases:case-detail", kwargs={"pk": case.id}),
    )
    assert response.status_code == 200
    assertContains(
        response,
        f"""<tr class="govuk-table__row">
            <th scope="row" class="govuk-table__header amp-width-one-half">Link to final PDF report</th>
            <td class="govuk-table__cell amp-width-one-half">
                <a href="{report_final_pdf_url}" rel="noreferrer noopener" target="_blank" class="govuk-link">
                    Final PDF draft
                </a>
            </td>
        </tr>""",
        html=True,
    )


def test_case_details_includes_no_link_to_report(admin_client):
    """
    Test that the case details page contains no link to the report if none is set
    """
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.get(
        reverse("cases:case-detail", kwargs={"pk": case.id}),
    )
    assert response.status_code == 200
    assertContains(
        response,
        """<tr class="govuk-table__row">
            <th scope="row" class="govuk-table__header amp-width-one-half">Link to final PDF report</th>
            <td class="govuk-table__cell amp-width-one-half">None</td>
        </tr>""",
        html=True,
    )


def test_status_change_message_shown(admin_client):
    """Test updating the case status causes a message to be shown on the next page"""
    user: User = User.objects.create()
    add_user_to_auditor_groups(user)

    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.post(
        reverse("cases:edit-case-details", kwargs={"pk": case.id}),
        {
            "auditor": user.id,
            "home_page_url": HOME_PAGE_URL,
            "enforcement_body": "ehrc",
            "save_continue": "Save and continue",
        },
        follow=True,
    )

    assert response.status_code == 200
    assertContains(
        response,
        """<div class="govuk-inset-text">
            Status changed from 'Unassigned case' to 'Test in progress'
        </div>""",
        html=True,
    )


def test_report_ready_to_review_with_no_report_error_messages(admin_client):
    """
    Test that the report details page shows the expected error messages
    when the report is set to ready to review while the link to report draft is empty
    """
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.post(
        reverse("cases:edit-report-details", kwargs={"pk": case.id}),
        {
            "report_draft_url": "",
            "report_review_status": "ready-to-review",
            "save_continue": "Save and continue",
        },
    )

    assert response.status_code == 200
    assertContains(
        response,
        """<ul class="govuk-list govuk-error-summary__list">
            <li><a href="#id_report_draft_url-label">Add link to report draft, if report is ready to be reviewed</a></li>
            <li><a href="#id_report_review_status-label">Report cannot be ready to be reviewed without a link to report draft</a></li>
        </ul>""",
        html=True,
    )
    assertContains(
        response,
        """<p class="govuk-error-message">
            <span class="govuk-visually-hidden">Error:</span>
            Add link to report draft, if report is ready to be reviewed
        </p>""",
        html=True,
    )
    assertContains(
        response,
        """<p class="govuk-error-message">
            <span class="govuk-visually-hidden">Error:</span>
            Report cannot be ready to be reviewed without a link to report draft
        </p>""",
        html=True,
    )


@pytest.mark.parametrize(
    "useful_link, edit_url_name",
    [
        ("zendesk_url", "edit-case-details"),
        ("trello_url", "edit-contact-details"),
        ("zendesk_url", "edit-test-results"),
        ("trello_url", "edit-report-details"),
        ("zendesk_url", "edit-report-correspondence"),
        ("trello_url", "edit-twelve-week-correspondence"),
        ("zendesk_url", "edit-final-decision"),
        ("trello_url", "edit-enforcement-body-correspondence"),
    ],
)
def test_useful_links_displayed_in_edit(useful_link, edit_url_name, admin_client):
    """
    Test that the useful links are displayed on all edit pages
    """
    case: Case = Case.objects.create(home_page_url="https://home_page_url.com")
    setattr(case, useful_link, f"https://{useful_link}.com")
    case.save()

    response: HttpResponse = admin_client.get(
        reverse(f"cases:{edit_url_name}", kwargs={"pk": case.id}),
    )

    assert response.status_code == 200

    assertContains(
        response,
        """<h2 class="govuk-heading-m bottom-margin-5">Case status</h2>
            <p class="govuk-body-m">Unassigned case</p>""",
        html=True,
    )

    assertContains(
        response,
        """<li>
            <a href="https://home_page_url.com" rel="noreferrer noopener" target="_blank" class="govuk-link">
                Link to website
            </a>
        </li>""",
        html=True,
    )

    if useful_link == "trello_url":
        assertContains(
            response,
            """<li>
                <a href="https://trello_url.com" rel="noreferrer noopener" target="_blank" class="govuk-link">
                    Trello
                </a>
            </li>""",
            html=True,
        )
        assertNotContains(
            response,
            """<li>
                <a href="https://zendesk_url.com" rel="noreferrer noopener" target="_blank" class="govuk-link">
                    Zendesk
                </a>
            </li>""",
            html=True,
        )
    else:
        assertNotContains(
            response,
            """<li>
                <a href="https://trello_url.com" rel="noreferrer noopener" target="_blank" class="govuk-link">
                    Trello
                </a>
            </li>""",
            html=True,
        )
        assertContains(
            response,
            """<li>
                <a href="https://zendesk_url.com" rel="noreferrer noopener" target="_blank" class="govuk-link">
                    Zendesk
                </a>
            </li>""",
            html=True,
        )


def test_case_reviewer_updated_when_active_user_sets_report_approved(
    admin_client, admin_user
):
    """
    Test that the case QA auditor is set to the current user when report is approved
    and the current user is an active QA auditor
    """
    case: Case = Case.objects.create()

    response: HttpResponse = admin_client.post(
        reverse("cases:edit-report-details", kwargs={"pk": case.id}),
        {
            "report_approved_status": "yes",
            "save_continue": "Save and continue",
        },
    )

    assert response.status_code == 302
    updated_case: Case = Case.objects.get(pk=case.id)
    assert updated_case.reviewer == admin_user


def test_case_final_decision_view_shows_warning_when_no_problems_found(admin_client):
    """
    Test that the case final decision view contains a warning if the website and accessibility statement
    are compliant
    """
    case: Case = Case.objects.create(
        is_website_compliant="compliant", accessibility_statement_state="compliant"
    )

    response: HttpResponse = admin_client.get(
        reverse("cases:edit-final-decision", kwargs={"pk": case.id})
    )

    assert response.status_code == 200
    assertContains(
        response,
        """<div class="govuk-warning-text">
            <span class="govuk-warning-text__icon" aria-hidden="true">!</span>
            <strong class="govuk-warning-text__text">
                <span class="govuk-warning-text__assistive">Warning</span>
                The public sector body website is compliant and has no issues with the accessibility statement.
                The case can be marked as completed with no further action.
            </strong>
        </div>""",
        html=True,
    )
