"""
Tests for audits views
"""
import pytest

from typing import Dict, List

from pytest_django.asserts import assertContains

from django.http import HttpResponse
from django.urls import reverse

from ...cases.models import Case
from ...common.models import BOOLEAN_TRUE, BOOLEAN_FALSE
from ..models import (
    PAGE_TYPE_ALL,
    Audit,
    Page,
    WcagDefinition,
    CheckResult,
    PAGE_TYPE_HOME,
    PAGE_TYPE_STATEMENT,
    PAGE_TYPE_EXTRA,
    TEST_TYPE_AXE,
    TEST_TYPE_MANUAL,
    TEST_TYPE_PDF,
)
from ..utils import create_pages_and_checks_for_new_audit

WCAG_TYPE_AXE_NAME: str = "WCAG Axe name"
WCAG_TYPE_MANUAL_NAME: str = "WCAG Manual name"
WCAG_TYPE_PDF_NAME: str = "WCAG PDF name"
EXTRA_PAGE_NAME: str = "Extra page name"
EXTRA_PAGE_URL: str = "https://extra-page.com"
CHECK_RESULT_NOTES: str = "Check result notes"


def create_audit() -> Audit:
    case: Case = Case.objects.create()
    audit: Audit = Audit.objects.create(case=case)
    return audit


def create_audit_and_pages() -> Audit:
    audit: Audit = create_audit()
    WcagDefinition.objects.create(type=TEST_TYPE_AXE, name=WCAG_TYPE_AXE_NAME)
    WcagDefinition.objects.create(type=TEST_TYPE_PDF, name=WCAG_TYPE_PDF_NAME)
    create_pages_and_checks_for_new_audit(audit=audit)
    return audit


def get_path_kwargs(audit: Audit, path_name: str) -> Dict[str, int]:
    if "-manual" in path_name or "-axe" in path_name:
        return {
            "audit_id": audit.id,  # type: ignore
            "page_id": audit.next_page.id,
        }
    return {
        "pk": audit.id,  # type: ignore
    }


def test_delete_audit_view(admin_client):
    """Test that delete audit view deletes audit"""
    audit: Audit = create_audit()

    response: HttpResponse = admin_client.post(
        reverse("audits:delete-audit", kwargs={"pk": audit.id}),  # type: ignore
        {
            "version": audit.version,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse(
        "cases:edit-test-results", kwargs={"pk": audit.case.id}
    )

    audit_from_db: Audit = Audit.objects.get(pk=audit.id)  # type: ignore

    assert audit_from_db.is_deleted


def test_restore_audit_view(admin_client):
    """Test that restore audit view restores audit"""
    audit: Audit = create_audit()
    audit.is_deleted = True
    audit.save()

    response: HttpResponse = admin_client.post(
        reverse("audits:restore-audit", kwargs={"pk": audit.id}),  # type: ignore
        {
            "version": audit.version,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("audits:audit-detail", kwargs={"pk": audit.id})  # type: ignore

    audit_from_db: Audit = Audit.objects.get(pk=audit.id)  # type: ignore

    assert audit_from_db.is_deleted is False


@pytest.mark.parametrize(
    "button_name, expected_redirect_url",
    [
        (
            "save_continue",
            reverse("audits:edit-audit-metadata", kwargs={"pk": 1}),
        ),
        ("save_exit", reverse("cases:edit-test-results", kwargs={"pk": 1})),
    ],
)
def test_create_audit_redirects_based_on_button_pressed(
    button_name, expected_redirect_url, admin_client
):
    """Test that audit create redirects based on the button pressed"""
    case: Case = Case.objects.create()
    path_kwargs: Dict[str, int] = {"case_id": case.id}  # type: ignore

    response: HttpResponse = admin_client.post(
        reverse("audits:audit-create", kwargs=path_kwargs),
        {
            button_name: "Button value",
        },
    )

    assert response.status_code == 302

    assert response.url == expected_redirect_url


@pytest.mark.parametrize(
    "path_name, expected_content",
    [
        ("audits:audit-detail", "View test"),
        ("audits:edit-audit-metadata", "Edit test | Test metadata"),
        ("audits:edit-audit-pages", "Edit test | Pages"),
        ("audits:edit-audit-pdf", "Edit test | PDF tests"),
        ("audits:edit-audit-statement-1", "Edit test | Accessibility statement Pt. 1"),
        ("audits:edit-audit-statement-2", "Edit test | Accessibility statement Pt. 2"),
        ("audits:edit-audit-summary", "Edit test | Test summary"),
        ("audits:edit-audit-report-options", "Edit test | Report options"),
        ("audits:edit-audit-report-text", "Edit test | Report text"),
    ],
)
def test_audit_specific_page_loads(path_name, expected_content, admin_client):
    """Test that the audit-specific view page loads"""
    audit: Audit = create_audit_and_pages()

    response: HttpResponse = admin_client.get(reverse(path_name, kwargs={"pk": audit.id}))  # type: ignore

    assert response.status_code == 200

    assertContains(response, expected_content)


@pytest.mark.parametrize(
    "path_name, expected_content",
    [
        ("audits:edit-audit-manual", "Edit test | Manual tests"),
        ("audits:edit-audit-axe", "Edit test | Axe and colour contrast tests"),
        ("audits:edit-audit-manual-axe", "Edit test | Manual and axe tests"),
    ],
)
def test_audit_page_specific_page_loads(path_name, expected_content, admin_client):
    """Test that the audit-page-specific view page loads"""
    audit: Audit = create_audit_and_pages()

    response: HttpResponse = admin_client.get(
        reverse(path_name, kwargs={"audit_id": audit.id, "page_id": audit.next_page.id})  # type: ignore
    )

    assert response.status_code == 200

    assertContains(response, expected_content)


@pytest.mark.parametrize(
    "path_name, button_name, expected_redirect_path_name, expected_view_page_anchor",
    [
        ("audits:edit-audit-metadata", "save_continue", "audits:edit-audit-pages", ""),
        (
            "audits:edit-audit-metadata",
            "save_exit",
            "audits:audit-detail",
            "#audit-metadata",
        ),
        ("audits:edit-audit-pages", "save_continue", "audits:edit-audit-manual", ""),
        ("audits:edit-audit-pages", "save_exit", "audits:audit-detail", "#audit-pages"),
        ("audits:edit-audit-manual", "save_continue", "audits:edit-audit-axe", ""),
        (
            "audits:edit-audit-manual",
            "save_exit",
            "audits:audit-detail",
            "#audit-manual",
        ),
        ("audits:edit-audit-axe", "save_continue", "audits:edit-audit-manual-axe", ""),
        ("audits:edit-audit-axe", "save_exit", "audits:audit-detail", "#audit-axe"),
        ("audits:edit-audit-manual-axe", "save_continue", "audits:edit-audit-pdf", ""),
        (
            "audits:edit-audit-manual-axe",
            "save_exit",
            "audits:audit-detail",
            "#audit-manual",
        ),
        ("audits:edit-audit-pdf", "save_continue", "audits:edit-audit-statement-1", ""),
        ("audits:edit-audit-pdf", "save_exit", "audits:audit-detail", "#audit-pdf"),
        (
            "audits:edit-audit-statement-1",
            "save_continue",
            "audits:edit-audit-statement-2",
            "",
        ),
        (
            "audits:edit-audit-statement-1",
            "save_exit",
            "audits:audit-detail",
            "#audit-statement",
        ),
        (
            "audits:edit-audit-statement-2",
            "save_continue",
            "audits:edit-audit-summary",
            "",
        ),
        (
            "audits:edit-audit-statement-2",
            "save_exit",
            "audits:audit-detail",
            "#audit-statement",
        ),
        (
            "audits:edit-audit-summary",
            "save_continue",
            "audits:edit-audit-report-options",
            "",
        ),
        ("audits:edit-audit-summary", "save_exit", "audits:audit-detail", ""),
        (
            "audits:edit-audit-report-options",
            "save_continue",
            "audits:edit-audit-report-text",
            "",
        ),
        (
            "audits:edit-audit-report-options",
            "save_exit",
            "audits:audit-detail",
            "#audit-report-options",
        ),
        (
            "audits:edit-audit-report-text",
            "save_exit",
            "audits:audit-detail",
            "#audit-report-text",
        ),
    ],
)
def test_audit_edit_redirects_based_on_button_pressed(
    path_name,
    button_name,
    expected_redirect_path_name,
    expected_view_page_anchor,
    admin_client,
):
    """Test that a successful audit update redirects based on the button pressed"""
    audit: Audit = create_audit_and_pages()

    response: HttpResponse = admin_client.post(
        reverse(path_name, kwargs=get_path_kwargs(audit=audit, path_name=path_name)),  # type: ignore
        {
            "version": audit.version,
            "next_page": audit.next_page.id,
            button_name: "Button value",
            "standard-TOTAL_FORMS": "0",
            "standard-INITIAL_FORMS": "0",
            "standard-MIN_NUM_FORMS": "0",
            "standard-MAX_NUM_FORMS": "1000",
            "extra-TOTAL_FORMS": "0",
            "extra-INITIAL_FORMS": "0",
            "extra-MIN_NUM_FORMS": "0",
            "extra-MAX_NUM_FORMS": "1000",
            "manual-TOTAL_FORMS": "0",
            "manual-INITIAL_FORMS": "0",
            "manual-MIN_NUM_FORMS": "0",
            "manual-MAX_NUM_FORMS": "1000",
            "axe-TOTAL_FORMS": "0",
            "axe-INITIAL_FORMS": "0",
            "axe-MIN_NUM_FORMS": "0",
            "axe-MAX_NUM_FORMS": "1000",
            "form-TOTAL_FORMS": "0",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
        },
    )

    assert response.status_code == 302

    expected_path: str = reverse(
        expected_redirect_path_name,
        kwargs=get_path_kwargs(audit=audit, path_name=expected_redirect_path_name),
    )
    assert response.url == f"{expected_path}{expected_view_page_anchor}"  # type: ignore


def test_standard_pages_appear_on_pages_page(admin_client):
    """
    Test that all the standard pages appear on the pages page
    """
    audit: Audit = create_audit_and_pages()

    response: HttpResponse = admin_client.get(
        reverse("audits:edit-audit-pages", kwargs={"pk": audit.id}),  # type: ignore
    )
    assert response.status_code == 200
    assertContains(
        response, """<h2 class="govuk-heading-m">Home Page</h2>""", html=True
    )
    assertContains(
        response, """<h2 class="govuk-heading-m">Contact Page</h2>""", html=True
    )
    assertContains(
        response,
        """<h2 class="govuk-heading-m">Accessibility Statement</h2>""",
        html=True,
    )
    assertContains(response, """<h2 class="govuk-heading-m">PDF</h2>""", html=True)
    assertContains(response, """<h2 class="govuk-heading-m">A Form</h2>""", html=True)


def test_add_extra_page_form_appears(admin_client):
    """
    Test that pressing the save and create additional page button adds an extra page form
    """
    audit: Audit = create_audit_and_pages()

    response: HttpResponse = admin_client.post(
        reverse("audits:edit-audit-pages", kwargs={"pk": audit.id}),  # type: ignore
        {
            "standard-TOTAL_FORMS": "0",
            "standard-INITIAL_FORMS": "0",
            "standard-MIN_NUM_FORMS": "0",
            "standard-MAX_NUM_FORMS": "1000",
            "extra-TOTAL_FORMS": "0",
            "extra-INITIAL_FORMS": "0",
            "extra-MIN_NUM_FORMS": "0",
            "extra-MAX_NUM_FORMS": "1000",
            "version": audit.version,
            "add_extra": "Button value",
        },
        follow=True,
    )
    assert response.status_code == 200
    assertContains(response, "Page 1")


def test_add_extra_page(admin_client):
    """Test adding an extra page"""
    audit: Audit = create_audit_and_pages()

    response: HttpResponse = admin_client.post(
        reverse("audits:edit-audit-pages", kwargs={"pk": audit.id}),  # type: ignore
        {
            "standard-TOTAL_FORMS": "0",
            "standard-INITIAL_FORMS": "0",
            "standard-MIN_NUM_FORMS": "0",
            "standard-MAX_NUM_FORMS": "1000",
            "extra-TOTAL_FORMS": "1",
            "extra-INITIAL_FORMS": "0",
            "extra-MIN_NUM_FORMS": "0",
            "extra-MAX_NUM_FORMS": "1000",
            "extra-0-id": "",
            "extra-0-name": EXTRA_PAGE_NAME,
            "extra-0-url": EXTRA_PAGE_URL,
            "version": audit.version,
            "save_continue": "Save and continue",
        },
        follow=True,
    )
    assert response.status_code == 200

    extra_pages: List[Page] = list(Page.objects.filter(audit=audit, type=PAGE_TYPE_EXTRA))  # type: ignore

    assert len(extra_pages) == 1
    assert extra_pages[0].name == EXTRA_PAGE_NAME
    assert extra_pages[0].url == EXTRA_PAGE_URL


def test_delete_extra_page(admin_client):
    """Test deleting an extra page"""
    audit: Audit = create_audit_and_pages()
    extra_page: Page = Page.objects.create(
        audit=audit,
        type=PAGE_TYPE_EXTRA,
    )

    response: HttpResponse = admin_client.post(
        reverse("audits:edit-audit-pages", kwargs={"pk": audit.id}),  # type: ignore
        {
            "standard-TOTAL_FORMS": "0",
            "standard-INITIAL_FORMS": "0",
            "standard-MIN_NUM_FORMS": "0",
            "standard-MAX_NUM_FORMS": "1000",
            "extra-TOTAL_FORMS": "0",
            "extra-INITIAL_FORMS": "0",
            "extra-MIN_NUM_FORMS": "0",
            "extra-MAX_NUM_FORMS": "1000",
            "version": audit.version,
            f"remove_extra_page_{extra_page.id}": "Remove page",  # type: ignore
        },
        follow=True,
    )
    assert response.status_code == 200

    updated_extra_page: Page = Page.objects.get(id=extra_page.id)  # type: ignore

    assert updated_extra_page.is_deleted


def test_manual_checks_displayed(admin_client):
    """Test manual checks are displayed on manual page"""
    audit: Audit = create_audit_and_pages()
    wcag_definition: WcagDefinition = WcagDefinition.objects.create(
        type=TEST_TYPE_MANUAL, sub_type="keyboard", name=WCAG_TYPE_MANUAL_NAME
    )
    CheckResult.objects.create(
        audit=audit,
        page=audit.next_page,
        type=wcag_definition.type,
        wcag_definition=wcag_definition,
    )

    response: HttpResponse = admin_client.get(
        reverse(
            "audits:edit-audit-manual",
            kwargs={"audit_id": audit.id, "page_id": audit.next_page.id},  # type: ignore
        ),
    )

    assert response.status_code == 200
    assertContains(response, WCAG_TYPE_MANUAL_NAME)


def test_updating_manual_check_result_while_switching_to_page_all(admin_client):
    """
    Test updating a manual check result while switching to all pages does not
    update check results for other pages.
    """
    wcag_definition_manual: WcagDefinition = WcagDefinition.objects.create(
        type=TEST_TYPE_MANUAL, name=WCAG_TYPE_MANUAL_NAME
    )
    audit: Audit = create_audit_and_pages()
    page_all: Page = Page.objects.get(audit=audit, type=PAGE_TYPE_ALL)
    check_result: CheckResult = CheckResult.objects.get(
        audit=audit, page=audit.next_page, type=TEST_TYPE_MANUAL
    )

    response: HttpResponse = admin_client.post(
        reverse(
            "audits:edit-audit-manual",
            kwargs={"audit_id": audit.id, "page_id": audit.next_page.id},  # type: ignore
        ),
        {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "1",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-version": check_result.version,
            "form-0-id": check_result.id,  # type: ignore
            "form-0-failed": "on",
            "form-0-notes": CHECK_RESULT_NOTES,
            "version": audit.version,
            "next_page": page_all.id,  # type: ignore
            "save_change_test_page": "Save and change test page",
        },
        follow=True,
    )
    assert response.status_code == 200

    updated_check_result: CheckResult = CheckResult.objects.get(
        audit=audit, page=audit.next_page, type=TEST_TYPE_MANUAL
    )

    assert updated_check_result.wcag_definition == wcag_definition_manual
    assert updated_check_result.notes == CHECK_RESULT_NOTES
    assert updated_check_result.failed == BOOLEAN_TRUE

    check_result_all: CheckResult = CheckResult.objects.get(
        audit=audit, page=page_all, type=TEST_TYPE_MANUAL
    )
    assert check_result_all.notes == ""
    assert check_result_all.failed == BOOLEAN_FALSE


def test_updating_manual_check_result_on_page_all(admin_client):
    """
    Test updating a manual check result to all pages updates check results
    for other pages.
    """
    wcag_definition_manual: WcagDefinition = WcagDefinition.objects.create(
        type=TEST_TYPE_MANUAL, name=WCAG_TYPE_MANUAL_NAME
    )
    audit: Audit = create_audit_and_pages()
    page_all: Page = Page.objects.get(audit=audit, type=PAGE_TYPE_ALL)
    audit.next_page = page_all
    audit.save()
    check_result_all: CheckResult = CheckResult.objects.get(
        audit=audit, page=audit.next_page, type=TEST_TYPE_MANUAL
    )
    page_home: Page = Page.objects.get(audit=audit, type=PAGE_TYPE_HOME)
    check_result_home: CheckResult = CheckResult.objects.get(
        audit=audit, page=page_home, type=TEST_TYPE_MANUAL
    )

    assert check_result_home.notes == ""
    assert check_result_home.failed == BOOLEAN_FALSE

    response: HttpResponse = admin_client.post(
        reverse(
            "audits:edit-audit-manual",
            kwargs={"audit_id": audit.id, "page_id": audit.next_page.id},  # type: ignore
        ),
        {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "1",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-version": check_result_all.version,
            "form-0-id": check_result_all.id,  # type: ignore
            "form-0-failed": "on",
            "form-0-notes": CHECK_RESULT_NOTES,
            "version": audit.version,
            "next_page": page_home.id,  # type: ignore
            "save_change_test_page": "Save and change test page",
        },
        follow=True,
    )
    assert response.status_code == 200

    updated_check_result_all: CheckResult = CheckResult.objects.get(
        audit=audit, page=audit.next_page, type=TEST_TYPE_MANUAL
    )

    assert updated_check_result_all.wcag_definition == wcag_definition_manual
    assert updated_check_result_all.notes == CHECK_RESULT_NOTES
    assert updated_check_result_all.failed == BOOLEAN_TRUE

    check_result_home: CheckResult = CheckResult.objects.get(
        audit=audit, page=page_home, type=TEST_TYPE_MANUAL
    )
    assert check_result_home.notes == CHECK_RESULT_NOTES
    assert check_result_home.failed == BOOLEAN_TRUE


def test_axe_checks_displayed(admin_client):
    """Test axe checks are displayed on axe page"""
    audit: Audit = create_audit_and_pages()
    wcag_definition: WcagDefinition = WcagDefinition.objects.get(
        type=TEST_TYPE_AXE, name=WCAG_TYPE_AXE_NAME
    )
    CheckResult.objects.create(
        audit=audit,
        page=audit.next_page,
        type=wcag_definition.type,
        wcag_definition=wcag_definition,
    )

    response: HttpResponse = admin_client.get(
        reverse(
            "audits:edit-audit-axe",
            kwargs={"audit_id": audit.id, "page_id": audit.next_page.id},  # type: ignore
        ),
    )

    assert response.status_code == 200
    assertContains(response, WCAG_TYPE_AXE_NAME)


@pytest.mark.parametrize(
    "path_name", ["audits:edit-audit-manual", "audits:edit-audit-axe"]
)
def test_changing_audit_next_page(path_name, admin_client):
    """Test changing the next page of an audit"""
    audit: Audit = create_audit_and_pages()
    home_page: Page = Page.objects.get(audit=audit, type=PAGE_TYPE_HOME)
    statement_page: Page = Page.objects.get(audit=audit, type=PAGE_TYPE_STATEMENT)

    assert audit.next_page == home_page

    response: HttpResponse = admin_client.post(
        reverse(
            path_name,
            kwargs={"audit_id": audit.id, "page_id": audit.next_page_id},  # type: ignore
        ),
        {
            "form-TOTAL_FORMS": "0",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "version": audit.version,
            "next_page": statement_page.id,  # type: ignore
            "save_change_test_page": "Save and change test page",  # type: ignore
        },
        follow=True,
    )
    assert response.status_code == 200

    updated_audit: Audit = Audit.objects.get(id=audit.id)  # type: ignore

    assert updated_audit.next_page == statement_page


def test_add_axe_check_result(admin_client):
    """Test adding an axe check result"""
    audit: Audit = create_audit_and_pages()
    wcag_definition_axe: WcagDefinition = WcagDefinition.objects.get(type=TEST_TYPE_AXE)

    response: HttpResponse = admin_client.post(
        reverse(
            "audits:edit-audit-axe",
            kwargs={"audit_id": audit.id, "page_id": audit.next_page.id},  # type: ignore
        ),
        {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": "",
            "form-0-wcag_definition": wcag_definition_axe.id,  # type: ignore
            "form-0-notes": CHECK_RESULT_NOTES,
            "version": audit.version,
            "next_page": audit.next_page.id,
            "save_change_test_page": "Save and change test page",
        },
        follow=True,
    )
    assert response.status_code == 200

    check_result: CheckResult = CheckResult.objects.get(
        audit=audit, page=audit.next_page, type=TEST_TYPE_AXE
    )

    assert check_result.wcag_definition == wcag_definition_axe
    assert check_result.notes == CHECK_RESULT_NOTES
    assert check_result.failed == BOOLEAN_TRUE


def test_add_axe_check_result_while_switching_to_page_all(admin_client):
    """
    Test adding an axe check result while switching to all pages does not
    create check results for other pages.
    """
    audit: Audit = create_audit_and_pages()
    wcag_definition_axe: WcagDefinition = WcagDefinition.objects.get(type=TEST_TYPE_AXE)
    page_all: Page = Page.objects.get(audit=audit, type=PAGE_TYPE_ALL)

    response: HttpResponse = admin_client.post(
        reverse(
            "audits:edit-audit-axe",
            kwargs={"audit_id": audit.id, "page_id": audit.next_page.id},  # type: ignore
        ),
        {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": "",
            "form-0-wcag_definition": wcag_definition_axe.id,  # type: ignore
            "form-0-notes": CHECK_RESULT_NOTES,
            "version": audit.version,
            "next_page": page_all.id,  # type: ignore
            "save_change_test_page": "Save and change test page",
        },
        follow=True,
    )
    assert response.status_code == 200

    check_result: CheckResult = CheckResult.objects.get(
        audit=audit, page=audit.next_page, type=TEST_TYPE_AXE
    )

    assert check_result.wcag_definition == wcag_definition_axe
    assert check_result.notes == CHECK_RESULT_NOTES
    assert check_result.failed == BOOLEAN_TRUE

    with pytest.raises(CheckResult.DoesNotExist):
        CheckResult.objects.get(audit=audit, page=page_all, type=TEST_TYPE_AXE)


def test_add_axe_check_result_on_page_all(admin_client):
    """
    Test adding an axe check result to all pages creates check results
    for other pages.
    """
    audit: Audit = create_audit_and_pages()
    wcag_definition_axe: WcagDefinition = WcagDefinition.objects.get(type=TEST_TYPE_AXE)
    page_all: Page = Page.objects.get(audit=audit, type=PAGE_TYPE_ALL)
    audit.next_page = page_all
    audit.save()

    page_home: Page = Page.objects.get(audit=audit, type=PAGE_TYPE_HOME)

    with pytest.raises(CheckResult.DoesNotExist):
        CheckResult.objects.get(audit=audit, page=page_home, type=TEST_TYPE_AXE)

    response: HttpResponse = admin_client.post(
        reverse(
            "audits:edit-audit-axe",
            kwargs={"audit_id": audit.id, "page_id": audit.next_page.id},  # type: ignore
        ),
        {
            "form-TOTAL_FORMS": "1",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "form-0-id": "",
            "form-0-wcag_definition": wcag_definition_axe.id,  # type: ignore
            "form-0-notes": CHECK_RESULT_NOTES,
            "version": audit.version,
            "next_page": audit.next_page.id,  # type: ignore
            "save_change_test_page": "Save and change test page",
        },
        follow=True,
    )
    assert response.status_code == 200

    check_result: CheckResult = CheckResult.objects.get(
        audit=audit, page=audit.next_page, type=TEST_TYPE_AXE
    )

    assert check_result.wcag_definition == wcag_definition_axe
    assert check_result.notes == CHECK_RESULT_NOTES
    assert check_result.failed == BOOLEAN_TRUE

    check_result_home: CheckResult = CheckResult.objects.get(
        audit=audit, page=page_home, type=TEST_TYPE_AXE
    )

    assert check_result_home.wcag_definition == wcag_definition_axe
    assert check_result_home.notes == CHECK_RESULT_NOTES
    assert check_result_home.failed == BOOLEAN_TRUE


def test_delete_axe_check_result(admin_client):
    """Test deleting an axe check result"""
    audit: Audit = create_audit_and_pages()
    wcag_definition_axe: WcagDefinition = WcagDefinition.objects.get(type=TEST_TYPE_AXE)
    check_result: CheckResult = CheckResult.objects.create(
        audit=audit,
        page=audit.next_page,
        type=TEST_TYPE_AXE,
        wcag_definition=wcag_definition_axe,
    )

    response: HttpResponse = admin_client.post(
        reverse(
            "audits:edit-audit-axe",
            kwargs={"audit_id": audit.id, "page_id": audit.next_page.id},  # type: ignore
        ),
        {
            "form-TOTAL_FORMS": "0",
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "0",
            "form-MAX_NUM_FORMS": "1000",
            "version": audit.version,
            "next_page": audit.next_page.id,
            f"remove_check_result_{check_result.id}": "Remove violation",  # type: ignore
        },
        follow=True,
    )
    assert response.status_code == 200

    updated_check_result: CheckResult = CheckResult.objects.get(id=check_result.id)  # type: ignore

    assert updated_check_result.is_deleted


def test_pdf_checks_displayed(admin_client):
    """Test pdf checks are displayed on pdf page"""
    audit: Audit = create_audit_and_pages()
    wcag_definition: WcagDefinition = WcagDefinition.objects.get(
        type=TEST_TYPE_PDF, name=WCAG_TYPE_PDF_NAME
    )
    CheckResult.objects.create(
        audit=audit,
        page=audit.next_page,
        type=wcag_definition.type,
        wcag_definition=wcag_definition,
    )

    response: HttpResponse = admin_client.get(
        reverse(
            "audits:edit-audit-pdf",
            kwargs={"pk": audit.id},  # type: ignore
        ),
    )

    assert response.status_code == 200
    assertContains(response, WCAG_TYPE_PDF_NAME)
