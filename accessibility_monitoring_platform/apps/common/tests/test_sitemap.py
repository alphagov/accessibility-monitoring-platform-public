"""
Test utility functions of cases app
"""

from datetime import date

import pytest
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from pytest_django.asserts import assertContains

from ...audits.models import Audit, Page, Retest, RetestPage
from ...cases.models import Case, Contact, EqualityBodyCorrespondence, ZendeskTicket
from ...comments.models import Comment
from ...common.models import EmailTemplate
from ...exports.models import Export
from ...notifications.models import Task
from ...reports.models import Report
from ..sitemap import (
    SITE_MAP,
    SITEMAP_BY_URL_NAME,
    AuditPagesPlatformPage,
    AuditPlatformPage,
    AuditRetestPagesPlatformPage,
    CaseCommentsPlatformPage,
    CaseContactsPlatformPage,
    CasePlatformPage,
    EqualityBodyRetestPagesPlatformPage,
    EqualityBodyRetestPlatformPage,
    ExportPlatformPage,
    HomePlatformPage,
    PlatformPage,
    PlatformPageGroup,
    ReportPlatformPage,
    RetestOverviewPlatformPage,
    Sitemap,
    build_sitemap_for_current_page,
    get_platform_page_name_by_url,
    get_requested_platform_page,
    get_subpages_by_url_name,
)

PLATFORM_PAGE_NAME: str = "Platform page name"
URL_NAME: str = "url-name"
ORGANISATION_NAME: str = "Organisation name"
EMAIL_TEMPLATE_NAME: str = "1c. Template name"
FIRST_SEPTEMBER_2024 = date(2024, 9, 1)


class MockRequest:
    def __init__(self, get_params=None):
        if get_params is None:
            self.GET = {}
        else:
            self.GET = get_params


def test_platform_page_url_kwarg_key():
    """
    Test PlatformPage url_kwarg_key defaults to "pk" if an object_class is set
    """
    assert PlatformPage(name=PLATFORM_PAGE_NAME).url_kwarg_key is None
    assert (
        PlatformPage(name=PLATFORM_PAGE_NAME, object_class=Case).url_kwarg_key == "pk"
    )


def test_platform_page_repr():
    """Test PlatformPage.__repr__()"""
    assert (
        PlatformPage(name=PLATFORM_PAGE_NAME).__repr__()
        == f'PlatformPage(name="{PLATFORM_PAGE_NAME}", url_name="None")'
    )
    assert (
        PlatformPage(name=PLATFORM_PAGE_NAME, url_name=URL_NAME).__repr__()
        == f'PlatformPage(name="{PLATFORM_PAGE_NAME}", url_name="{URL_NAME}")'
    )
    assert (
        PlatformPage(
            name=PLATFORM_PAGE_NAME, url_name=URL_NAME, object_class=Case
        ).__repr__()
        == f'PlatformPage(name="{PLATFORM_PAGE_NAME}", url_name="{URL_NAME}", object_class="<class \'accessibility_monitoring_platform.apps.cases.models.Case\'>")'
    )


def test_platform_page_url():
    """Test PlatformPage.url"""
    assert PlatformPage(name=PLATFORM_PAGE_NAME).url is None
    assert (
        PlatformPage(name=PLATFORM_PAGE_NAME, url_name="cases:case-list").url
        == "/cases/"
    )

    case: Case = Case(id=1)

    assert (
        PlatformPage(
            name="Case metadata",
            url_name="cases:edit-case-metadata",
            object_class=Case,
            object=case,
        ).url
        == "/cases/1/edit-case-metadata/"
    )


def test_platform_page_url_missing_object():
    """Test PlatformPage.url returns empty string when a required object is missing"""
    assert (
        PlatformPage(
            name=PLATFORM_PAGE_NAME, url_name=URL_NAME, object_required_for_url=True
        ).url
        == ""
    )


def test_platform_page_show():
    """Test PlatformPage.show"""
    assert PlatformPage(name=PLATFORM_PAGE_NAME).show is True
    assert PlatformPage(name=PLATFORM_PAGE_NAME, object_class=Case).show is True

    case: Case = Case(organisation_name="Show flag")

    assert (
        PlatformPage(
            name=PLATFORM_PAGE_NAME,
            object_class=Case,
            object=case,
            show_flag_name="organisation_name",
        ).show
        == "Show flag"
    )


def test_platform_page_complete():
    """Test PlatformPage.complete"""
    assert PlatformPage(name=PLATFORM_PAGE_NAME).complete is None

    case: Case = Case(organisation_name="complete flag")

    assert (
        PlatformPage(
            name=PLATFORM_PAGE_NAME,
            object_class=Case,
            object=case,
            complete_flag_name="organisation_name",
        ).complete
        == "complete flag"
    )


def test_platform_page_populate_subpage_objects():
    """
    Test PlatformPage.populate_subpage_objects() populates subpages with objects
    """
    case: Case = Case()

    platform_page: PlatformPage = PlatformPage(
        name=PLATFORM_PAGE_NAME,
        object=case,
        object_class=Case,
        subpages=[
            PlatformPage(name=PLATFORM_PAGE_NAME, object_class=Case),
            PlatformPage(name=PLATFORM_PAGE_NAME, object_class=Case),
            PlatformPage(name=PLATFORM_PAGE_NAME, object_class=Audit),
        ],
    )

    platform_page.populate_subpage_objects()

    assert len(platform_page.subpages) == 3
    assert platform_page.subpages[0].object == case
    assert platform_page.subpages[1].object == case
    assert platform_page.subpages[2].object is None


def test_platform_page_populate_from_case():
    """
    Test PlatformPage.populate_from_case() populates subpages with objects
    """
    case: Case = Case()

    platform_page: PlatformPage = PlatformPage(
        name=PLATFORM_PAGE_NAME,
        object=case,
        object_class=Case,
        subpages=[
            CasePlatformPage(name=PLATFORM_PAGE_NAME),
            CasePlatformPage(name=PLATFORM_PAGE_NAME),
            AuditPlatformPage(name=PLATFORM_PAGE_NAME),
        ],
    )

    platform_page.populate_from_case(case=case)

    assert len(platform_page.subpages) == 3
    assert platform_page.subpages[0].object == case
    assert platform_page.subpages[1].object == case
    assert platform_page.subpages[2].object is None


@pytest.mark.django_db
def test_populate_from_request(rf):
    """Test PlatformPage.populate_from_request sets the object"""
    case: Case = Case.objects.create()
    contact: Contact = Contact.objects.create(case=case, name="Contact name")

    request_user: User = User.objects.create(
        username="johnsmith", first_name="John", last_name="Smith"
    )
    request = rf.get(
        reverse("cases:edit-contact-update", kwargs={"pk": contact.id}),
    )
    request.user = request_user

    platform_page: PlatformPage = PlatformPage(
        name="Edit contact {object}",
        url_name="cases:edit-contact-update",
        object_required_for_url=True,
        object_class=Contact,
    )

    platform_page.populate_from_request(request=request)

    assert platform_page.object == contact
    assert platform_page.get_name() == "Edit contact Contact name"
    assert platform_page.url == f"/cases/contacts/{contact.id}/edit-contact-update/"


def test_platform_page_get_name():
    """Test PlatformPage.get_name()"""
    assert PlatformPage(name=PLATFORM_PAGE_NAME).get_name() == PLATFORM_PAGE_NAME

    case: Case = Case(organisation_name=ORGANISATION_NAME)

    assert (
        PlatformPage(
            name="{object.organisation_name}",
            object=case,
        ).get_name()
        == ORGANISATION_NAME
    )


def test_platform_page_get_case():
    """Test PlatformPage.get_case()"""
    assert PlatformPage(name=PLATFORM_PAGE_NAME).get_case() is None

    case: Case = Case()

    assert PlatformPage(name=PLATFORM_PAGE_NAME, object=case).get_case() == case

    audit: Audit = Audit(case=case)

    assert PlatformPage(name=PLATFORM_PAGE_NAME, object=audit).get_case() == case
    page: Page = Page(audit=audit)

    assert PlatformPage(name=PLATFORM_PAGE_NAME, object=page).get_case() == case

    retest: Retest = Retest(case=case)
    retest_page: RetestPage = RetestPage(retest=retest)

    assert PlatformPage(name=PLATFORM_PAGE_NAME, object=retest_page).get_case() == case


def test_home_platform_page():
    """Test HomePlatformPage sets name based on GET parameters"""
    home_platform_page: HomePlatformPage = HomePlatformPage(name=PLATFORM_PAGE_NAME)

    mock_request: MockRequest = MockRequest()

    home_platform_page.populate_from_request(request=mock_request)

    assert home_platform_page.get_name() == "Your cases"

    mock_request: MockRequest = MockRequest({"view": "View all cases"})

    home_platform_page.populate_from_request(request=mock_request)

    assert home_platform_page.get_name() == "All cases"

    mock_request: MockRequest = MockRequest({"view": "View your cases"})

    home_platform_page.populate_from_request(request=mock_request)

    assert home_platform_page.get_name() == "Your cases"


def test_export_platform_page():
    """Test ExportPlatformPage sets name based on GET parameters"""
    export_platform_page: ExportPlatformPage = ExportPlatformPage(
        name="{enforcement_body} CSV export manager"
    )

    mock_request: MockRequest = MockRequest()

    export_platform_page.populate_from_request(request=mock_request)

    assert export_platform_page.get_name() == "EHRC CSV export manager"

    mock_request: MockRequest = MockRequest({"enforcement_body": "ecni"})

    export_platform_page.populate_from_request(request=mock_request)

    assert export_platform_page.get_name() == "ECNI CSV export manager"

    mock_request: MockRequest = MockRequest({"enforcement_body": "ehrc"})

    export_platform_page.populate_from_request(request=mock_request)

    assert export_platform_page.get_name() == "EHRC CSV export manager"


def test_case_platform_page():
    """Test CasePlatformPage"""
    case_platform_page: CasePlatformPage = CasePlatformPage(name=PLATFORM_PAGE_NAME)

    assert case_platform_page.object_required_for_url is True
    assert case_platform_page.object_class == Case
    assert case_platform_page.url_kwarg_key == "pk"

    case: Case = Case()

    case_platform_page.populate_from_case(case=case)

    assert case_platform_page.object == case


@pytest.mark.django_db
def test_case_comments_platform_page():
    """Test CaseCommentsPlatformPage"""
    case_comments_platform_page: CaseCommentsPlatformPage = CaseCommentsPlatformPage(
        name="Comments",
        url_name="cases:edit-qa-comments",
    )

    assert case_comments_platform_page.object_required_for_url is True
    assert case_comments_platform_page.object_class == Case
    assert case_comments_platform_page.url_kwarg_key == "pk"

    case: Case = Case.objects.create()
    user: User = User.objects.create()
    Comment.objects.create(case=case, user=user, body="Comment One")
    Comment.objects.create(case=case, user=user, body="Comment Two")

    case_comments_platform_page.populate_from_case(case=case)

    assert case_comments_platform_page.object == case
    assert len(case_comments_platform_page.subpages) == 2
    assert (
        case_comments_platform_page.subpages[0].get_name() == "Edit or delete comment"
    )
    assert (
        case_comments_platform_page.subpages[1].get_name() == "Edit or delete comment"
    )


@pytest.mark.django_db
def test_case_contacts_platform_page():
    """Test CaseContactsPlatformPage"""
    case_contacts_platform_page: CaseContactsPlatformPage = CaseContactsPlatformPage(
        name="Manage contact details",
        url_name="cases:manage-contact-details",
    )

    assert case_contacts_platform_page.object_required_for_url is True
    assert case_contacts_platform_page.object_class == Case
    assert case_contacts_platform_page.url_kwarg_key == "pk"

    case: Case = Case.objects.create()
    Contact.objects.create(case=case, name="Contact One")
    Contact.objects.create(case=case, name="Contact Two")

    case_contacts_platform_page.populate_from_case(case=case)

    assert case_contacts_platform_page.object == case
    assert len(case_contacts_platform_page.subpages) == 3
    assert case_contacts_platform_page.subpages[0].get_name() == "Add contact"
    assert (
        case_contacts_platform_page.subpages[1].get_name() == "Edit contact Contact Two"
    )
    assert (
        case_contacts_platform_page.subpages[2].get_name() == "Edit contact Contact One"
    )


@pytest.mark.django_db
def test_audit_platform_page():
    """Test AuditPlatformPage"""
    audit_platform_page: AuditPlatformPage = AuditPlatformPage(name=PLATFORM_PAGE_NAME)

    assert audit_platform_page.object_required_for_url is True
    assert audit_platform_page.object_class == Audit
    assert audit_platform_page.url_kwarg_key == "pk"

    case: Case = Case.objects.create()
    audit: Audit = Audit.objects.create(case=case)

    audit_platform_page.populate_from_case(case=case)

    assert audit_platform_page.object == audit


@pytest.mark.django_db
def test_audit_pages_platform_page():
    """Test AuditPagesPlatformPage"""
    audit_pages_platform_page: AuditPagesPlatformPage = AuditPagesPlatformPage(
        name="Add or remove pages",
        url_name="audits:edit-audit-pages",
    )

    assert audit_pages_platform_page.object_required_for_url is True
    assert audit_pages_platform_page.object_class == Audit
    assert audit_pages_platform_page.url_kwarg_key == "pk"

    case: Case = Case.objects.create()
    audit: Audit = Audit.objects.create(case=case)
    Page.objects.create(audit=audit, name="Page one", url="url")
    Page.objects.create(audit=audit, name="Page two", url="url")

    audit_pages_platform_page.populate_from_case(case=case)

    assert audit_pages_platform_page.object == audit
    assert len(audit_pages_platform_page.subpages) == 2
    assert audit_pages_platform_page.subpages[0].get_name() == "Page one page test (0)"
    assert audit_pages_platform_page.subpages[1].get_name() == "Page two page test (0)"


@pytest.mark.django_db
def test_report_platform_page():
    """Test ReportPlatformPage"""
    report_platform_page: ReportPlatformPage = ReportPlatformPage(
        name=PLATFORM_PAGE_NAME
    )

    assert report_platform_page.object_required_for_url is True
    assert report_platform_page.object_class == Report
    assert report_platform_page.url_kwarg_key == "pk"

    case: Case = Case.objects.create()
    report: Report = Report.objects.create(case=case)

    report_platform_page.populate_from_case(case=case)

    assert report_platform_page.object == report


@pytest.mark.django_db
def test_audit_retest_pages_platform_page():
    """Test AuditRetestPagesPlatformPage"""
    audit_retest_pages_platform_page: AuditRetestPagesPlatformPage = (
        AuditRetestPagesPlatformPage(
            name="Pages",
            url_name="audits:edit-audit-retest-pages",
        )
    )

    assert audit_retest_pages_platform_page.object_required_for_url is True
    assert audit_retest_pages_platform_page.object_class == Audit
    assert audit_retest_pages_platform_page.url_kwarg_key == "pk"

    case: Case = Case.objects.create()
    audit: Audit = Audit.objects.create(case=case)
    Page.objects.create(audit=audit, name="Page one", url="url")
    Page.objects.create(audit=audit, name="Page two", url="url")

    audit_retest_pages_platform_page.populate_from_case(case=case)

    assert audit_retest_pages_platform_page.object == audit
    assert len(audit_retest_pages_platform_page.subpages) == 2
    assert (
        audit_retest_pages_platform_page.subpages[0].get_name()
        == "Page one page retest"
    )
    assert (
        audit_retest_pages_platform_page.subpages[1].get_name()
        == "Page two page retest"
    )


def test_equality_body_retest_platform_page():
    """Test EqualityBodyRetestPlatformPage"""
    equality_body_retest_platform_page: EqualityBodyRetestPlatformPage = (
        EqualityBodyRetestPlatformPage(name=PLATFORM_PAGE_NAME)
    )

    assert equality_body_retest_platform_page.object_required_for_url is True
    assert equality_body_retest_platform_page.object_class == Retest
    assert equality_body_retest_platform_page.url_kwarg_key == "pk"


@pytest.mark.django_db
def test_retest_overview_platform_page():
    """Test RetestOverviewPlatformPage"""
    retest_overview_platform_page: RetestOverviewPlatformPage = (
        RetestOverviewPlatformPage(
            name="Retest overview",
            url_name="cases:edit-retest-overview",
        )
    )

    assert retest_overview_platform_page.object_required_for_url is True
    assert retest_overview_platform_page.object_class == Case
    assert retest_overview_platform_page.url_kwarg_key == "pk"

    case: Case = Case.objects.create()
    Retest.objects.create(case=case, id_within_case=0)
    Retest.objects.create(case=case, id_within_case=1)
    Retest.objects.create(case=case, id_within_case=2)

    retest_overview_platform_page.populate_from_case(case=case)

    assert retest_overview_platform_page.object == case
    assert len(retest_overview_platform_page.subpages) == 2
    assert retest_overview_platform_page.subpages[0].get_name() == "Retest #2"
    assert retest_overview_platform_page.subpages[1].get_name() == "Retest #1"


@pytest.mark.django_db
def test_equality_body_retest_pages_platform_page():
    """Test EqualityBodyRetestPagesPlatformPage"""
    equality_body_retest_pages_platform_page: EqualityBodyRetestPagesPlatformPage = (
        EqualityBodyRetestPagesPlatformPage(
            name="Pages",
            subpages=[
                PlatformPage(
                    name="{object.retest} | {object}",
                    url_name="audits:edit-retest-page-checks",
                    object_class=RetestPage,
                    complete_flag_name="complete_date",
                )
            ],
        )
    )

    assert equality_body_retest_pages_platform_page.object_required_for_url is True
    assert equality_body_retest_pages_platform_page.object_class == Retest
    assert equality_body_retest_pages_platform_page.url_kwarg_key == "pk"

    case: Case = Case.objects.create()
    audit: Audit = Audit.objects.create(case=case)
    page: Page = Page.objects.create(audit=audit, name="Test Page")
    retest: Retest = Retest.objects.create(case=case, id_within_case=1)
    RetestPage.objects.create(retest=retest, page=page)
    RetestPage.objects.create(retest=retest, page=page)

    equality_body_retest_pages_platform_page.object = retest
    equality_body_retest_pages_platform_page.populate_subpage_objects()

    assert len(equality_body_retest_pages_platform_page.subpages) == 2
    assert (
        equality_body_retest_pages_platform_page.subpages[0].get_name()
        == f"{retest} | {page}"
    )
    assert (
        equality_body_retest_pages_platform_page.subpages[1].get_name()
        == f"{retest} | {page}"
    )


@pytest.mark.django_db
def test_retest_overview_platform_page_populates_subpages():
    """Test RetestOverviewPlatformPage populates subpages from case"""
    case: Case = Case.objects.create()
    audit: Audit = Audit.objects.create(case=case)
    page_1: Page = Page.objects.create(audit=audit, name="Test page one")
    page_2: Page = Page.objects.create(audit=audit, name="Test page two")
    retest: Retest = Retest.objects.create(case=case, id_within_case=1)
    RetestPage.objects.create(retest=retest, page=page_1)
    RetestPage.objects.create(retest=retest, page=page_2)

    retest_overview_platform_page: RetestOverviewPlatformPage = (
        RetestOverviewPlatformPage(
            name="Retest overview",
            url_name="cases:edit-retest-overview",
        )
    )
    retest_overview_platform_page.populate_from_case(case=case)

    assert retest_overview_platform_page.object == case
    assert len(retest_overview_platform_page.subpages) == 1
    assert retest_overview_platform_page.subpages[0].get_name() == "Retest #1"

    retest_1: PlatformPage = retest_overview_platform_page.subpages[0]

    assert len(retest_1.subpages) > 2
    assert retest_1.subpages[1].get_name() == "Pages"

    retest_1_pages: PlatformPage = retest_1.subpages[1]

    assert len(retest_1_pages.subpages) == 2
    assert retest_1_pages.subpages[0].get_name() == f"{retest} | {page_1}"
    assert retest_1_pages.subpages[1].get_name() == f"{retest} | {page_2}"


@pytest.mark.django_db
def test_get_requested_platform_page_for_case(rf):
    """Test get_requested_platform_page returns expected Case-specific page"""
    case: Case = Case.objects.create()

    request_user: User = User.objects.create(
        username="johnsmith", first_name="John", last_name="Smith"
    )
    request = rf.get(
        reverse("cases:edit-case-metadata", kwargs={"pk": case.id}),
    )
    request.user = request_user

    current_platform_page: PlatformPage = get_requested_platform_page(request)

    assert current_platform_page.get_name() == "Case metadata"
    assert current_platform_page.url_name == "cases:edit-case-metadata"


@pytest.mark.django_db
def test_get_requested_platform_page_for_page(rf):
    """Test get_requested_platform_page returns expected Page-specific page"""
    case: Case = Case.objects.create()
    audit: Audit = Audit.objects.create(case=case)
    page: Page = Page.objects.create(audit=audit)

    request_user: User = User.objects.create(
        username="johnsmith", first_name="John", last_name="Smith"
    )
    request = rf.get(
        reverse("audits:edit-audit-page-checks", kwargs={"pk": page.id}),
    )
    request.user = request_user

    current_platform_page: PlatformPage = get_requested_platform_page(request)

    assert current_platform_page.get_name() == "Additional page test (0)"
    assert current_platform_page.url_name == "audits:edit-audit-page-checks"


@pytest.mark.django_db
def test_get_requested_platform_page_for_retest_page(rf):
    """Test get_requested_platform_page returns expected RetestPage-specific page"""
    case: Case = Case.objects.create()
    audit: Audit = Audit.objects.create(case=case)
    page: Page = Page.objects.create(audit=audit)
    retest: Retest = Retest.objects.create(case=case)
    retest_page: RetestPage = RetestPage.objects.create(retest=retest, page=page)

    request_user: User = User.objects.create(
        username="johnsmith", first_name="John", last_name="Smith"
    )
    request = rf.get(
        reverse("audits:edit-retest-page-checks", kwargs={"pk": retest_page.id}),
    )
    request.user = request_user

    current_platform_page: PlatformPage = get_requested_platform_page(request)

    assert current_platform_page.get_name() == "Retest #1 | Additional"
    assert current_platform_page.url_name == "audits:edit-retest-page-checks"


@pytest.mark.django_db
def test_get_requested_platform_page_for_email_template(rf):
    """Test get_requested_platform_page returns expected EmailTemplate-specific name"""
    case: Case = Case.objects.create()
    email_template: EmailTemplate = EmailTemplate.objects.create(
        name=EMAIL_TEMPLATE_NAME
    )

    request_user: User = User.objects.create(
        username="johnsmith", first_name="John", last_name="Smith"
    )
    request = rf.get(
        reverse(
            "cases:email-template-preview",
            kwargs={"pk": email_template.id, "case_id": case.id},
        ),
    )
    request.user = request_user

    current_platform_page: PlatformPage = get_requested_platform_page(request)

    assert current_platform_page.get_name() == EMAIL_TEMPLATE_NAME
    assert current_platform_page.url_name == "cases:email-template-preview"


@pytest.mark.django_db
def test_get_requested_platform_page_with_extra_context(rf):
    """Test get_requested_platform_page returns expected name with extra context"""
    request_user: User = User.objects.create(
        username="johnsmith", first_name="John", last_name="Smith"
    )
    request = rf.get(
        reverse("exports:export-list"),
    )
    request.user = request_user

    current_platform_page: PlatformPage = get_requested_platform_page(request)

    assert current_platform_page.get_name() == "EHRC CSV export manager"
    assert current_platform_page.url_name == "exports:export-list"

    request = rf.get(
        f'{reverse("exports:export-list")}?enforcement_body=ecni',
    )

    current_platform_page: PlatformPage = get_requested_platform_page(request)

    assert current_platform_page.get_name() == "ECNI CSV export manager"
    assert current_platform_page.url_name == "exports:export-list"


def test_sitemap_by_url_name():
    """Test SITEMAP_BY_URL_NAME has been built correctly"""
    assert isinstance(SITEMAP_BY_URL_NAME, dict) is True

    assert "cases:edit-case-metadata" in SITEMAP_BY_URL_NAME
    assert SITEMAP_BY_URL_NAME["cases:edit-case-metadata"].get_name() == "Case metadata"


def test_get_subpages_by_url_name():
    """Test get_subpages_by_url_name returns expected subpages"""

    assert get_subpages_by_url_name("cases:edit-case-metadata") is None

    subpages: list[PlatformPage] = get_subpages_by_url_name(
        "audits:edit-statement-overview"
    )

    assert subpages is not None
    assert len(subpages) > 0
    assert subpages[0].name == "Statement information"


def test_build_sitemap_for_non_case_current_page():
    """Test build_sitemap_for_current_page when current page is not Case-related"""
    platform_page: PlatformPage = PlatformPage(
        name="Test", url_name="common:platform-checking"
    )
    platform_page_groups: list[PlatformPageGroup] = build_sitemap_for_current_page(
        current_platform_page=platform_page
    )

    assert platform_page_groups == SITE_MAP


@pytest.mark.django_db
def test_build_sitemap_for_case_related_current_page():
    """Test build_sitemap_for_current_page when current page is Case-related"""
    case: Case = Case.objects.create()
    platform_page: PlatformPage = PlatformPage(
        name="Test", url_name="cases:case-metadata", object_class=Case, object=case
    )
    platform_page_groups: list[PlatformPageGroup] = build_sitemap_for_current_page(
        current_platform_page=platform_page
    )

    assert len(platform_page_groups) < len(SITE_MAP)
    assert len(platform_page_groups) > 0

    platform_page_group: PlatformPageGroup = platform_page_groups[0]

    assert platform_page_group.pages is not None
    assert len(platform_page_group.pages) > 0

    platform_page: PlatformPage = platform_page_group.pages[0]

    assert platform_page.get_case() == case


def test_non_case_sitemap(rf):
    """Test non-Case sitemap creation"""
    request: HttpRequest = rf.get("/")
    sitemap: Sitemap = Sitemap(request=request)

    assert sitemap.current_platform_page is not None
    assert sitemap.platform_page_groups is not None

    assert sitemap.current_platform_page.get_case() is None
    assert len(sitemap.platform_page_groups) == len(SITE_MAP)


@pytest.mark.django_db
def test_case_sitemap(rf):
    """Test Case-specific sitemap creation"""
    case: Case = Case.objects.create()
    request: HttpRequest = rf.get("/cases/1/view/")
    sitemap: Sitemap = Sitemap(request=request)

    assert sitemap.current_platform_page is not None
    assert sitemap.platform_page_groups is not None

    assert sitemap.current_platform_page.get_case() == case
    assert len(sitemap.platform_page_groups) < len(SITE_MAP)


@pytest.mark.django_db
def test_get_platform_page_name_by_url():
    """Test get_platform_page_name_by_url returns the name of the page"""

    assert get_platform_page_name_by_url("/") == "Your cases"
    assert (
        get_platform_page_name_by_url("/account/login/")
        == "Page name not found for two_factor:login"
    )
    assert get_platform_page_name_by_url("/x/") == "URL not found for /x/"

    case: Case = Case.objects.create()
    audit: Audit = Audit.objects.create(case=case)
    page: Page = Page.objects.create(audit=audit, name="PSB page one")

    assert (
        get_platform_page_name_by_url(
            f"/audits/pages/{page.id}/edit-audit-page-checks/"
        )
        == f"{page.page_title} test (0)"
    )


@pytest.mark.parametrize(
    "url, expected_page_name",
    [
        ("/", "Your cases"),
        ("/cases/1/edit-case-metadata/", "Case metadata"),
        ("/audits/1/edit-audit-metadata/", "Initial test metadata"),
        ("/audits/pages/1/edit-audit-page-checks/", "Pagename page test"),
        (
            "/cases/contacts/1/edit-contact-update/",
            "Edit contact Contact Name a.b@example.com",
        ),
        ("/audits/retests/1/retest-metadata-update/", "Retest #1 | Retest metadata"),
        ("/audits/retest-pages/1/retest-page-checks/", "Retest #1 | Pagename"),
        ("/notifications/cases/1/reminder-task-create/", "Reminder"),
        ("/notifications/1/edit-reminder-task/", "Reminder"),
        ("/cases/1/edit-equality-body-correspondence/", "Edit Zendesk ticket"),
        ("/cases/1/update-zendesk-ticket/", "Edit PSB Zendesk ticket"),
        ("/cases/1/1/email-template-preview/", "12-week update request"),
        ("/comments/1/edit-qa-comment/", "Edit or delete comment"),
        ("/exports/export-create/?enforcement_body=ecni", "New ECNI CSV export"),
        ("/exports/1/export-detail/", "EHRC CSV export 1 September 2024"),
        ("/user/1/edit-user/", "Account details"),
        ("/common/edit-active-qa-auditor/", "Active QA auditor"),
        ("/audits/1/edit-wcag-definition/", "Update WCAG definition"),
        ("/audits/1/edit-statement-check/", "Update statement issue"),
        ("/common/1/email-template-preview/", "12-week update request preview"),
    ],
)
def test_page_name(url, expected_page_name, admin_client):
    """
    Test that the page renders and its name is as expected.
    Also that an issue on that page can be reported.
    """
    case: Case = Case.objects.create()
    audit: Audit = Audit.objects.create(case=case)
    page: Page = Page.objects.create(audit=audit, name="Pagename")
    Report.objects.create(case=case)
    Contact.objects.create(case=case, name="Contact Name", email="a.b@example.com")
    retest: Retest = Retest.objects.create(case=case)
    RetestPage.objects.create(retest=retest, page=page)
    user: User = User.objects.create()
    Task.objects.create(case=case, date=FIRST_SEPTEMBER_2024, user=user)
    EqualityBodyCorrespondence.objects.create(case=case)
    ZendeskTicket.objects.create(case=case)
    Comment.objects.create(case=case, user=user)
    Export.objects.create(cutoff_date=FIRST_SEPTEMBER_2024, exporter=user)

    response: HttpResponse = admin_client.get(url)
    assert response.status_code == 200

    assertContains(response, expected_page_name)

    issue_report_response: HttpResponse = admin_client.get(
        f"/common/report-issue/?page_url={url}"
    )

    assert issue_report_response.status_code == 200

    assertContains(response, "Report an issue")
    assertContains(response, url)
    assertContains(response, expected_page_name)
