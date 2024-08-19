"""
Test utility functions of cases app
"""

import csv
import io
from datetime import date, datetime, timezone
from typing import Any, List, Tuple

import pytest
from django.http import HttpResponse

from ...audits.models import Audit
from ...cases.models import Case, Contact
from ..csv_export_utils import (
    CASE_COLUMNS_FOR_EXPORT,
    EQUALITY_BODY_COLUMNS_FOR_EXPORT,
    FEEDBACK_SURVEY_COLUMNS_FOR_EXPORT,
    CSVColumn,
    EqualityBodyCSVColumn,
    download_cases,
    download_equality_body_cases,
    download_feedback_survey_cases,
    format_contacts,
    format_field_as_yes_no,
    format_model_field,
    populate_csv_columns,
    populate_equality_body_columns,
)

CONTACTS: List[Contact] = [
    Contact(
        name="Name 1",
        job_title="Job title 1",
        email="email1",
    ),
    Contact(
        name="Name 2",
        job_title="Job title 2",
        email="email2",
    ),
]
EXPECTED_FORMATTED_CONTACTS: str = """Name 1
Job title 1
email1

Name 2
Job title 2
email2
"""

CSV_EXPORT_FILENAME: str = "cases_export.csv"
CONTACT_NOTES: str = "Contact notes"
CONTACT_EMAIL: str = "example@example.com"


def decode_csv_response(response: HttpResponse) -> Tuple[List[str], List[List[str]]]:
    """Decode CSV HTTP response and break into column names and data"""
    content: str = response.content.decode("utf-8")
    cvs_reader: Any = csv.reader(io.StringIO(content))
    csv_body: List[List[str]] = list(cvs_reader)
    csv_header: List[str] = csv_body.pop(0)
    return csv_header, csv_body


def validate_csv_response(
    csv_header: List[str],
    csv_body: List[List[str]],
    expected_header: List[str],
    expected_first_data_row: List[str],
):
    """Validate csv header and body matches expected data"""
    assert csv_header == expected_header

    first_data_row: List[str] = csv_body[0]

    for position in range(len(first_data_row)):
        assert (
            first_data_row[position] == expected_first_data_row[position]
        ), f"Data mismatch on column {position}: {expected_header[position]}"

    assert first_data_row == expected_first_data_row


def test_format_case_field_with_no_data():
    """
    Test that format_model_field returns empty string if no model instance
    """
    assert (
        format_model_field(
            source_instance=None,
            column=CSVColumn(column_header="A", source_class=Case, source_attr="a"),
        )
        == ""
    )


@pytest.mark.parametrize(
    "column, case_value, expected_formatted_value",
    [
        (
            CSVColumn(
                column_header="Test type", source_class=Case, source_attr="test_type"
            ),
            "simplified",
            "Simplified",
        ),
        (
            CSVColumn(
                column_header="Report sent on",
                source_class=Case,
                source_attr="report_sent_date",
            ),
            date(2020, 12, 31),
            "31/12/2020",
        ),
        (
            CSVColumn(
                column_header="Enforcement recommendation",
                source_class=Case,
                source_attr="recommendation_for_enforcement",
            ),
            "no-further-action",
            "No further action",
        ),
        (
            CSVColumn(
                column_header="Which equality body will check the case",
                source_class=Case,
                source_attr="enforcement_body",
            ),
            "ehrc",
            "EHRC",
        ),
    ],
)
def test_format_case_field(column, case_value, expected_formatted_value):
    """Test that case fields are formatted correctly"""
    case: Case = Case()
    setattr(case, column.source_attr, case_value)
    assert expected_formatted_value == format_model_field(
        source_instance=case, column=column
    )


def test_format_field_as_yes_no():
    """Test field formatted as Yes if it contains a truthy value, otherwise No"""
    case: Case = Case()

    assert (
        format_field_as_yes_no(
            source_instance=case,
            column=CSVColumn(
                column_header="Falsey field",
                source_class=Case,
                source_attr="report_sent_date",
            ),
        )
        == "No"
    )
    assert (
        format_field_as_yes_no(
            source_instance=case,
            column=CSVColumn(
                column_header="Truthy field", source_class=Case, source_attr="test_type"
            ),
        )
        == "Yes"
    )


def test_format_contacts():
    """Test that contacts fields values are contatenated"""
    assert format_contacts(contacts=CONTACTS) == EXPECTED_FORMATTED_CONTACTS


@pytest.mark.django_db
def test_download_feedback_survey_cases():
    """Test creation of CSV for feedback survey"""
    case: Case = Case.objects.create(
        compliance_email_sent_date=datetime(2022, 12, 16, tzinfo=timezone.utc),
        contact_notes=CONTACT_NOTES,
    )
    cases: List[Case] = [case]

    response: HttpResponse = download_feedback_survey_cases(
        cases=cases, filename=CSV_EXPORT_FILENAME
    )

    assert response.status_code == 200

    assert response.headers == {
        "Content-Type": "text/csv",
        "Content-Disposition": f"attachment; filename={CSV_EXPORT_FILENAME}",
    }

    csv_header, csv_body = decode_csv_response(response)

    expected_header: List[str] = [
        column.column_header for column in FEEDBACK_SURVEY_COLUMNS_FOR_EXPORT
    ]
    expected_first_data_row: List[str] = [
        "1",  # Case no.
        "",  # Organisation name
        "16/12/2022",  # Closing the case date
        "Not selected",  # Enforcement recommendation
        "",  # Enforcement recommendation notes
        "",  # Contact email
        CONTACT_NOTES,  # Contact notes
        "No",  # Feedback survey sent
    ]

    validate_csv_response(
        csv_header=csv_header,
        csv_body=csv_body,
        expected_header=expected_header,
        expected_first_data_row=expected_first_data_row,
    )


@pytest.mark.django_db
def test_download_equality_body_cases():
    """Test creation of CSV for equality bodies"""
    case: Case = Case.objects.create()
    cases: List[Case] = [case]
    Audit.objects.create(
        case=case,
        archive_audit_retest_disproportionate_burden_notes="Audit for CSV export",
    )

    response: HttpResponse = download_equality_body_cases(
        cases=cases, filename=CSV_EXPORT_FILENAME
    )

    assert response.status_code == 200

    assert response.headers == {
        "Content-Type": "text/csv",
        "Content-Disposition": f"attachment; filename={CSV_EXPORT_FILENAME}",
    }

    csv_header, csv_body = decode_csv_response(response)

    expected_header: List[str] = [
        column.column_header for column in EQUALITY_BODY_COLUMNS_FOR_EXPORT
    ]

    expected_first_data_row: List[str] = [
        "EHRC",
        "Simplified",
        "1",
        "",
        "",
        "",
        "",
        "",
        "",
        "No",
        "",
        "Not selected",
        "",
        "",
        "",
        "No",
        "",
        "",
        "",
        "",
        "",
        "",
        "0",
        "0",
        "0",
        "n/a",
        "unknown",
        "unknown",
        "Not assessed",
        "Not assessed",
        "Not checked",
        "",
        "Not checked",
        "",
    ]

    validate_csv_response(
        csv_header=csv_header,
        csv_body=csv_body,
        expected_header=expected_header,
        expected_first_data_row=expected_first_data_row,
    )


@pytest.mark.django_db
def test_download_cases():
    """Test creation of CSV download of cases"""
    case: Case = Case.objects.create(
        created=datetime(2022, 12, 16, tzinfo=timezone.utc),
        contact_notes="Contact for CSV export",
    )
    cases: List[Case] = [case]
    Contact.objects.create(case=case, email="test@example.com")

    response: HttpResponse = download_cases(cases=cases, filename=CSV_EXPORT_FILENAME)

    assert response.status_code == 200

    assert response.headers == {
        "Content-Type": "text/csv",
        "Content-Disposition": f"attachment; filename={CSV_EXPORT_FILENAME}",
    }

    csv_header, csv_body = decode_csv_response(response)

    expected_header: List[str] = [
        column.column_header for column in CASE_COLUMNS_FOR_EXPORT
    ]

    expected_first_data_row: List[str] = [
        "1",
        "1",
        "",
        "16/12/2022",
        "Unassigned case",
        "",
        "Simplified",
        "",
        "",
        "",
        "Unknown",
        "",
        "EHRC",
        "No",
        "",
        "",
        "",
        "",
        "Not assessed",
        "",
        "Not known",
        "",
        "",
        "",
        "",
        "",
        "No",
        "",
        "Not started",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "No",
        "",
        "",
        "",
        "",
        "Not applicable or organisation responded to 12-week update",
        "",
        "",
        "",
        "",
        "",
        "No",
        "",
        "Not known",
        "",
        "",
        "Not known",
        "",
        "",
        "Not assessed",
        "",
        "",
        "Not selected",
        "",
        "",
        "Case still in progress",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "No",
        "",
        "",
        "False",
        "",
        "",
        "Unknown",
        "Contact for CSV export",
        "",
        "n/a",
        "",
        "",
        "",
        "test@example.com",
    ]

    validate_csv_response(
        csv_header=csv_header,
        csv_body=csv_body,
        expected_header=expected_header,
        expected_first_data_row=expected_first_data_row,
    )


@pytest.mark.django_db
def test_populate_equality_body_columns():
    """Test collection of case data for equality body export"""
    case: Case = Case.objects.create()
    Contact.objects.create(case=case, email=CONTACT_EMAIL)
    row: List[CSVColumn] = populate_equality_body_columns(case=case)

    assert len(row) == 34

    contact_details: List[EqualityBodyCSVColumn] = [
        cell for cell in row if cell.column_header == "Contact details"
    ]

    assert len(contact_details) == 1

    contact_details_cell: EqualityBodyCSVColumn = contact_details[0]

    assert contact_details_cell.formatted_data == f"{CONTACT_EMAIL}\n"
    assert contact_details_cell.edit_url_name == "cases:manage-contact-details"
    assert contact_details_cell.edit_url == "/cases/1/manage-contact-details/"

    organisation_responded: List[EqualityBodyCSVColumn] = [
        cell
        for cell in row
        if cell.column_header == "Organisation responded to report?"
    ]

    assert len(organisation_responded) == 1

    organisation_responded_cell: EqualityBodyCSVColumn = organisation_responded[0]

    assert organisation_responded_cell.formatted_data == "No"
    assert organisation_responded_cell.edit_url_name == "cases:edit-report-acknowledged"
    assert (
        organisation_responded_cell.edit_url
        == "/cases/1/edit-report-acknowledged/#id_report_acknowledged_date-label"
    )


@pytest.mark.django_db
def test_populate_csv_columns():
    """Test collection of case data for CSV export"""
    case: Case = Case.objects.create()
    Contact.objects.create(case=case, email=CONTACT_EMAIL)
    row: List[CSVColumn] = populate_csv_columns(
        case=case, column_definitions=CASE_COLUMNS_FOR_EXPORT
    )

    assert len(row) == 91

    contact_email: List[CSVColumn] = [
        cell for cell in row if cell.column_header == "Contact email"
    ]

    assert len(contact_email) == 1

    contact_email_cell: CSVColumn = contact_email[0]

    assert contact_email_cell.formatted_data == CONTACT_EMAIL


@pytest.mark.django_db
def test_populate_feedback_survey_columns():
    """Test collection of case data for feedback survey export"""
    case: Case = Case.objects.create()
    Contact.objects.create(case=case, email=CONTACT_EMAIL)
    row: List[CSVColumn] = populate_csv_columns(
        case=case, column_definitions=FEEDBACK_SURVEY_COLUMNS_FOR_EXPORT
    )

    assert len(row) == 8
