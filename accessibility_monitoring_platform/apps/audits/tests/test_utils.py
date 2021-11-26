"""
Test - common utility functions
"""
import pytest
from typing import List, Tuple

from django.contrib.auth.models import User
from django.db.models import QuerySet

from ...cases.models import Case
from ...common.form_extract_utils import FieldLabelAndValue
from ...common.models import BOOLEAN_TRUE

from ..models import (
    Audit,
    CheckResult,
    Page,
    WcagDefinition,
    PAGE_TYPE_HOME,
    PAGE_TYPE_CONTACT,
    PAGE_TYPE_STATEMENT,
    PAGE_TYPE_PDF,
    PAGE_TYPE_FORM,
    PAGE_TYPE_ALL,
    TEST_TYPE_PDF,
    TEST_TYPE_MANUAL,
)
from ..utils import (
    create_pages_and_checks_for_new_audit,
    create_check_results_for_new_page,
    copy_all_pages_check_results,
    get_audit_metadata_rows,
    get_audit_check_results_by_wcag,
    get_audit_pdf_rows,
    get_audit_statement_rows,
    get_audit_report_options_rows,
)

USER_FIRST_NAME = "John"
USER_LAST_NAME = "Smith"
TYPES_OF_OF_PAGES_CREATED_WITH_NEW_AUDIT: List[str] = [
    PAGE_TYPE_HOME,
    PAGE_TYPE_CONTACT,
    PAGE_TYPE_STATEMENT,
    PAGE_TYPE_PDF,
    PAGE_TYPE_FORM,
    PAGE_TYPE_ALL,
]
NUMBER_OF_PAGES_CREATED_WITH_NEW_AUDIT: int = len(
    TYPES_OF_OF_PAGES_CREATED_WITH_NEW_AUDIT
)
WCAG_TYPE_PDF_NAME: str = "PDF WCAG"
WCAG_TYPE_MANUAL_NAME: str = "Manual WCAG"
NUMBER_OF_WCAG_PER_TYPE_OF_PAGE: int = 1
NUMBER_OF_HTML_PAGES: int = 4
UPDATED_NOTE: str = "Updated note"
EXPECTED_AUDIT_METADATA_ROWS: List[FieldLabelAndValue] = [
    FieldLabelAndValue(
        value=None, label="Date of test", type="text", extra_label="", external_url=True
    ),
    FieldLabelAndValue(
        value="John Smith",
        label="Auditor",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="",
        label="Test description",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="15 inch",
        label="Screen size",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Unknown",
        label="Exemptions?",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Initial",
        label="Initital test or equality body retest?",
        type="text",
        extra_label="",
        external_url=True,
    ),
]
EXPECTED_AUDIT_PDF_ROWS: List[FieldLabelAndValue] = [
    FieldLabelAndValue(
        value="", label="PDF WCAG", type="notes", extra_label="", external_url=True
    )
]
EXPECTED_AUDIT_STATEMENT_ROWS: List[FieldLabelAndValue] = [
    FieldLabelAndValue(
        value="",
        label="Link to saved accessibility statement",
        type="url",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Not included",
        label="Declaration",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Not included",
        label="Scope",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Not present",
        label="Compliance Status",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Not present",
        label="Non-accessible Content - non compliance with regulations",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No claim",
        label="Non-accessible Content - disproportionate burden",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Not present",
        label="Non-accessible Content - the content is not within the scope of the applicable legislation",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Not included",
        label="Preparation Date",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Not present",
        label="Method",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Not included",
        label="Review",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Not present",
        label="Feedback",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Not present",
        label="Contact Information",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Not included",
        label="Contact Information",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Does not meet requirements",
        label="Access Requirements",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Not Compliant",
        label="Overall Decision on Compliance",
        type="text",
        extra_label="",
        external_url=True,
    ),
]
EXPECTED_AUDIT_REPORT_OPTIONS_ROWS: List[FieldLabelAndValue] = [
    FieldLabelAndValue(
        value="An accessibility statement for the website was not found.",
        label="Accessibility statement",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="It was not in the correct format",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="It was not specific enough",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="Accessibility issues were found during the test that were not included in the statement",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="Mandatory wording is missing",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="We require more information covering the disproportionate burden claim",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="It required more information detailing the accessibility issues",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="It includes a deadline of XXX for fixing XXX issues and this has not been completed",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="It includes a deadline of XXX for fixing XXX issues and this is not sufficient",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="It is out of date and needs to be reviewed",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="It is a requirement that accessibility statements are accessible. Some users may experience difficulties using PDF documents. It may be beneficial for users if there was a HTML version of your full accessibility statement.",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="In 2020 the GOV.UK sample template was updated to include an extra mandatory piece of information to outline the scope of your accessibility statement. This needs to be added to your statement.",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="Your statement should be prominently placed on the homepage of the website or made available on every web page, for example in a static header or footer, as per the legislative requirement.",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="Errors were found",
        label="What to do next",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="They have an acceptable statement but need to change it because of the errors we found",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="They don’t have a statement, or it is in the wrong format",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="They have a statement but it is not quite right",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="Their statement matches",
        type="text",
        extra_label="",
        external_url=True,
    ),
    FieldLabelAndValue(
        value="No",
        label="Disproportionate burden",
        type="text",
        extra_label="",
        external_url=True,
    ),
]


def create_audit_and_wcag() -> Audit:
    """Create an audit and WcagDefinitions"""
    case: Case = Case.objects.create()
    audit: Audit = Audit.objects.create(case=case)
    WcagDefinition.objects.create(type=TEST_TYPE_PDF, name=WCAG_TYPE_PDF_NAME)
    WcagDefinition.objects.create(type=TEST_TYPE_MANUAL, name=WCAG_TYPE_MANUAL_NAME)
    return audit


def create_audit_and_pages() -> Tuple[Audit, User]:
    """Create an audit and pages"""
    audit: Audit = create_audit_and_wcag()
    user: User = User.objects.create(
        first_name=USER_FIRST_NAME, last_name=USER_LAST_NAME
    )
    audit.case.auditor = user
    audit.case.save()
    create_pages_and_checks_for_new_audit(audit=audit, user=user)
    return audit, user


@pytest.mark.django_db
def test_create_pages_and_checks_for_new_audit():
    """Test creation of related pages and check results for new audit"""
    audit: Audit = create_audit_and_wcag()
    user: User = User.objects.create()

    create_pages_and_checks_for_new_audit(audit=audit, user=user)

    new_pages: QuerySet[Page] = Page.objects.filter(audit=audit)

    assert len(new_pages) == NUMBER_OF_PAGES_CREATED_WITH_NEW_AUDIT

    new_pages_types: List[str] = [page.type for page in new_pages]

    for page_type in TYPES_OF_OF_PAGES_CREATED_WITH_NEW_AUDIT:
        assert page_type in new_pages_types

    for new_page in new_pages:
        check_results: List[CheckResult] = list(new_page.checkresult_page.all())  # type: ignore
        assert len(check_results) == NUMBER_OF_WCAG_PER_TYPE_OF_PAGE

        if check_results[0].type == TEST_TYPE_PDF:
            assert check_results[0].wcag_definition.name == WCAG_TYPE_PDF_NAME
        elif check_results[0].type == TEST_TYPE_MANUAL:
            assert check_results[0].wcag_definition.name == WCAG_TYPE_MANUAL_NAME

    new_home_page: Page = Page.objects.get(audit=audit, type=PAGE_TYPE_HOME)
    updated_audit: Audit = Audit.objects.get(id=audit.id)  # type: ignore

    assert updated_audit.next_page == new_home_page


@pytest.mark.django_db
def test_create_check_results_for_new_page():
    """Test creation of check results for new page"""
    audit: Audit = create_audit_and_wcag()
    page: Page = Page.objects.create(audit=audit, type=PAGE_TYPE_HOME)
    user: User = User.objects.create()

    create_check_results_for_new_page(page=page, user=user)

    check_results: List[CheckResult] = list(page.checkresult_page.all())  # type: ignore

    assert len(check_results) == NUMBER_OF_WCAG_PER_TYPE_OF_PAGE

    assert check_results[0].wcag_definition.name == WCAG_TYPE_MANUAL_NAME


@pytest.mark.django_db
def test_copy_all_pages_check_results():
    """Test copy of check results to all html pages"""
    audit, user = create_audit_and_pages()
    page_all: Page = audit.page_audit.get(type=PAGE_TYPE_ALL)  # type: ignore
    check_results_all: List[CheckResult] = list(page_all.checkresult_page.all())  # type: ignore
    for check_result in check_results_all:
        check_result.notes = UPDATED_NOTE

    copy_all_pages_check_results(
        user=user, audit=audit, check_results=check_results_all
    )

    assert len(audit.html_pages) == NUMBER_OF_HTML_PAGES

    for page in audit.html_pages:
        check_results: QuerySet[CheckResult] = page.checkresult_page.all()
        assert len(check_results) == NUMBER_OF_WCAG_PER_TYPE_OF_PAGE
        for check_result in check_results:
            assert check_result.notes == UPDATED_NOTE


@pytest.mark.django_db
def test_get_audit_metadata_rows():
    """Test audit metadata rows returned for display on View test page"""
    audit, _ = create_audit_and_pages()

    assert get_audit_metadata_rows(audit=audit) == EXPECTED_AUDIT_METADATA_ROWS


@pytest.mark.django_db
def test_get_audit_check_results_by_wcag():
    """Test audit check results grouped by WCAG definition"""
    audit, _ = create_audit_and_pages()
    home_page: Page = audit.page_audit.get(type=PAGE_TYPE_HOME)  # type: ignore
    wcag_definition_manual: WcagDefinition = WcagDefinition.objects.get(
        type=TEST_TYPE_MANUAL
    )
    check_result_manual: CheckResult = home_page.checkresult_page.get(type=TEST_TYPE_MANUAL)  # type: ignore
    check_result_manual.failed = BOOLEAN_TRUE
    check_result_manual.save()

    audit_check_results: List[
        Tuple[WcagDefinition, List[CheckResult]]
    ] = get_audit_check_results_by_wcag(audit=audit, test_type=TEST_TYPE_MANUAL)

    assert len(audit_check_results) == 1

    wcag_definition, check_results = audit_check_results[0]

    assert wcag_definition == wcag_definition_manual

    assert isinstance(check_results, list)
    assert len(check_results) == NUMBER_OF_WCAG_PER_TYPE_OF_PAGE
    assert check_results[0] == check_result_manual


@pytest.mark.django_db
def test_get_audit_pdf_rows():
    """Test audit pdf rows returned for display on View test page"""
    audit, _ = create_audit_and_pages()
    check_result: CheckResult = audit.checkresult_audit.filter(type=TEST_TYPE_PDF).first()  # type: ignore
    check_result.failed = BOOLEAN_TRUE
    check_result.save()

    assert get_audit_pdf_rows(audit=audit) == EXPECTED_AUDIT_PDF_ROWS


@pytest.mark.django_db
def test_get_audit_statement_rows():
    """Test audit statement rows returned for display on View test page"""
    audit: Audit = create_audit_and_wcag()

    assert get_audit_statement_rows(audit=audit) == EXPECTED_AUDIT_STATEMENT_ROWS


@pytest.mark.django_db
def test_get_audit_report_options_rows():
    """Test audit report options rows returned for display on View test page"""
    audit: Audit = create_audit_and_wcag()

    assert (
        get_audit_report_options_rows(audit=audit) == EXPECTED_AUDIT_REPORT_OPTIONS_ROWS
    )
