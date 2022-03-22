"""
Tests for reports models
"""
import pytest
from datetime import datetime

from ...cases.models import Case

from ..models import Report, Section, PublishedReport


@pytest.mark.django_db
def test_report_created_timestamp_is_populated():
    """Test the Report created field is populated the first time the Report is saved"""
    case: Case = Case.objects.create()
    report: Report = Report.objects.create(case=case)

    assert report.created is not None
    assert isinstance(report.created, datetime)


@pytest.mark.django_db
def test_report_created_timestamp_is_not_updated():
    """Test the Report created field is not updated on subsequent saves"""
    case: Case = Case.objects.create()
    report: Report = Report.objects.create(case=case)

    original_created_timestamp: datetime = report.created
    report.save()
    updated_report: Report = Report.objects.get(pk=case.id)  # type: ignore

    assert updated_report.created == original_created_timestamp


@pytest.mark.django_db
def test_section_has_anchor():
    """Test the Section has an anchor property"""
    case: Case = Case.objects.create()
    report: Report = Report.objects.create(case=case)
    section: Section = Section.objects.create(report=report, position=1)

    assert section.anchor == f"report-section-{section.id}"  # type: ignore


@pytest.mark.django_db
def test_published_report_created_timestamp_is_populated():
    """
    Test the PublishedReport created field is populated on creation
    """
    case: Case = Case.objects.create()
    report: Report = Report.objects.create(case=case)
    published_report: PublishedReport = PublishedReport.objects.create(report=report)

    assert published_report.created is not None
    assert isinstance(published_report.created, datetime)
