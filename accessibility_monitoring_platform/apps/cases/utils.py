"""
Utility functions for cases app
"""

import copy
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from functools import partial
from typing import Any

from django import forms
from django.contrib.auth.models import User
from django.db.models import Case as DjangoCase
from django.db.models import Q, QuerySet, When
from django.http.request import QueryDict
from django.urls import reverse

from ..audits.models import Audit
from ..common.form_extract_utils import (
    FieldLabelAndValue,
    extract_form_labels_and_values,
)
from ..common.sitemap import PlatformPage, Sitemap
from ..common.utils import build_filters
from .models import COMPLIANCE_FIELDS, Case, CaseEvent, CaseStatus, Complaint, Sort

CASE_FIELD_AND_FILTER_NAMES: list[tuple[str, str]] = [
    ("auditor", "auditor_id"),
    ("reviewer", "reviewer_id"),
    ("status", "status"),
    ("sector", "sector_id"),
    ("subcategory", "subcategory_id"),
]


@dataclass
class CaseDetailPage:
    page: PlatformPage
    display_fields: list[FieldLabelAndValue] = None


@dataclass
class CaseDetailSection:
    page_group_name: str
    pages: list[CaseDetailPage]


def get_case_detail_sections(case: Case, sitemap: Sitemap) -> list[CaseDetailSection]:
    """Get sections for case view"""
    get_case_rows: Callable = partial(extract_form_labels_and_values, instance=case)
    get_audit_rows: Callable = partial(
        extract_form_labels_and_values, instance=case.audit
    )
    view_sections: list[CaseDetailSection] = []
    for page_group in sitemap.platform_page_groups:
        if page_group.show:
            case_detail_pages: list[CaseDetailPage] = []
            for page in page_group.pages:
                if page.show:
                    display_fields: list[FieldLabelAndValue] = []
                    if page.case_details_form_class:
                        if page.case_details_form_class._meta.model == Case:
                            display_fields = get_case_rows(
                                form=page.case_details_form_class()
                            )
                        if page.case_details_form_class._meta.model == Audit:
                            display_fields = get_audit_rows(
                                form=page.case_details_form_class()
                            )
                    if page.case_details_template_name:
                        case_detail_pages.append(
                            CaseDetailPage(
                                page=page,
                                display_fields=display_fields,
                            )
                        )
                    if page.subpages is not None:
                        for subpage in page.subpages:
                            if subpage.case_details_template_name:
                                case_detail_pages.append(
                                    CaseDetailPage(
                                        page=subpage,
                                    )
                                )
            view_sections.append(
                CaseDetailSection(
                    page_group_name=page_group.name, pages=case_detail_pages
                )
            )
    return view_sections


def get_sent_date(
    form: forms.ModelForm, case_from_db: Case, sent_date_name: str
) -> date | None:
    """
    Work out what value to save in a sent date field on the case.
    If there is a new value in the form, don't replace an existing date on the database.
    If there is a new value in the form and no date on the database then use the date from the form.
    If there is no value in the form (i.e. the checkbox is unchecked), set the date on the database to None.
    """
    date_on_form: date | None = form.cleaned_data.get(sent_date_name)
    if date_on_form is None:
        return None
    date_on_db: date = getattr(case_from_db, sent_date_name)
    return date_on_db if date_on_db else date_on_form


def filter_cases(form) -> QuerySet[Case]:  # noqa: C901
    """Return a queryset of Cases filtered by the values in CaseSearchForm"""
    filters: dict = {}
    search_query = Q()
    sort_by: str = Sort.NEWEST

    if hasattr(form, "cleaned_data"):
        field_and_filter_names: list[tuple[str, str]] = copy.copy(
            CASE_FIELD_AND_FILTER_NAMES
        )
        if "date_type" in form.cleaned_data:
            date_range_field: str = form.cleaned_data["date_type"]
            field_and_filter_names.append(("date_start", f"{date_range_field}__gte"))
            field_and_filter_names.append(("date_end", f"{date_range_field}__lte"))
        filters: dict[str, Any] = build_filters(
            cleaned_data=form.cleaned_data,
            field_and_filter_names=field_and_filter_names,
        )
        sort_by: str = form.cleaned_data.get("sort_by", Sort.NEWEST)
        if form.cleaned_data.get("case_search"):
            search: str = form.cleaned_data["case_search"]
            if (
                search.isdigit()
            ):  # if its just a number, it presumes its an ID and returns that case
                search_query = Q(case_number=search)
            else:
                search_query = (
                    Q(  # pylint: disable=unsupported-binary-operation
                        organisation_name__icontains=search
                    )
                    | Q(home_page_url__icontains=search)
                    | Q(psb_location__icontains=search)
                    | Q(sector__name__icontains=search)
                    | Q(parental_organisation_name__icontains=search)
                    | Q(website_name__icontains=search)
                    | Q(subcategory__name__icontains=search)
                )
        for filter_name in ["is_complaint", "enforcement_body"]:
            filter_value: str = form.cleaned_data.get(filter_name, Complaint.ALL)
            if filter_value != Complaint.ALL:
                filters[filter_name] = filter_value

    if str(filters.get("status", "")) == CaseStatus.Status.READY_TO_QA:
        filters["qa_status"] = CaseStatus.Status.READY_TO_QA
        del filters["status"]

    if "status" in filters:
        filters["status__status"] = filters["status"]
        del filters["status"]

    # Auditor and reviewer may be filtered by unassigned
    if "auditor_id" in filters and filters["auditor_id"] == "none":
        filters["auditor_id"] = None
    if "reviewer_id" in filters and filters["reviewer_id"] == "none":
        filters["reviewer_id"] = None

    if not sort_by:
        return (
            Case.objects.filter(search_query, **filters)
            .annotate(
                position_unassigned_first=DjangoCase(
                    When(status__status=CaseStatus.Status.UNASSIGNED, then=0), default=1
                )
            )
            .order_by("position_unassigned_first", "-id")
            .select_related("auditor", "reviewer")
        )
    return (
        Case.objects.filter(search_query, **filters)
        .order_by(sort_by)
        .select_related("auditor", "reviewer")
    )


def replace_search_key_with_case_search(request_get: QueryDict) -> dict[str, str]:
    """Convert QueryDict to dictionary and replace key 'search' with 'case_search'."""
    search_args: dict[str, str] = {key: value for key, value in request_get.items()}
    if "search" in search_args:
        search_args["case_search"] = search_args.pop("search")
    return search_args


def record_case_event(user: User, new_case: Case, old_case: Case | None = None) -> None:
    """Create a case event based on the changes between the old and new cases"""
    if old_case is None:
        CaseEvent.objects.create(
            case=new_case, done_by=user, event_type=CaseEvent.EventType.CREATE
        )
        return
    if old_case.auditor != new_case.auditor:
        old_user_name: str = (
            old_case.auditor.get_full_name() if old_case.auditor is not None else "none"
        )
        new_user_name: str = (
            new_case.auditor.get_full_name() if new_case.auditor is not None else "none"
        )
        CaseEvent.objects.create(
            case=old_case,
            done_by=user,
            event_type=CaseEvent.EventType.AUDITOR,
            message=f"Auditor changed from {old_user_name} to {new_user_name}",
        )
    if old_case.audit is None and new_case.audit is not None:
        CaseEvent.objects.create(
            case=old_case,
            done_by=user,
            event_type=CaseEvent.EventType.CREATE_AUDIT,
            message="Start of test",
        )
    if old_case.report_review_status != new_case.report_review_status:
        old_status: str = old_case.get_report_review_status_display()
        new_status: str = new_case.get_report_review_status_display()
        CaseEvent.objects.create(
            case=old_case,
            done_by=user,
            event_type=CaseEvent.EventType.READY_FOR_QA,
            message=f"Report ready to be reviewed changed from '{old_status}' to '{new_status}'",
        )
    if old_case.reviewer != new_case.reviewer:
        old_user_name: str = (
            old_case.reviewer.get_full_name()
            if old_case.reviewer is not None
            else "none"
        )
        new_user_name: str = (
            new_case.reviewer.get_full_name()
            if new_case.reviewer is not None
            else "none"
        )
        CaseEvent.objects.create(
            case=old_case,
            done_by=user,
            event_type=CaseEvent.EventType.QA_AUDITOR,
            message=f"QA auditor changed from {old_user_name} to {new_user_name}",
        )
    if old_case.report_approved_status != new_case.report_approved_status:
        old_status: str = old_case.get_report_approved_status_display()
        new_status: str = new_case.get_report_approved_status_display()
        CaseEvent.objects.create(
            case=old_case,
            done_by=user,
            event_type=CaseEvent.EventType.APPROVE_REPORT,
            message=f"QA approval changed from '{old_status}' to '{new_status}'",
        )
    if old_case.is_ready_for_final_decision != new_case.is_ready_for_final_decision:
        old_status: str = old_case.get_is_ready_for_final_decision_display()
        new_status: str = new_case.get_is_ready_for_final_decision_display()
        CaseEvent.objects.create(
            case=old_case,
            done_by=user,
            event_type=CaseEvent.EventType.READY_FOR_FINAL_DECISION,
            message=f"Case ready for final decision changed from '{old_status}' to '{new_status}'",
        )
    if old_case.case_completed != new_case.case_completed:
        old_status: str = old_case.get_case_completed_display()
        new_status: str = new_case.get_case_completed_display()
        CaseEvent.objects.create(
            case=old_case,
            done_by=user,
            event_type=CaseEvent.EventType.CASE_COMPLETED,
            message=f"Case completed changed from '{old_status}' to '{new_status}'",
        )


def build_edit_link_html(case: Case, url_name: str) -> str:
    """Return html of edit link for case"""
    case_pk: dict[str, int] = {"pk": case.id}
    edit_url: str = reverse(url_name, kwargs=case_pk)
    return (
        f"<a href='{edit_url}' class='govuk-link govuk-link--no-visited-state'>Edit</a>"
    )


def create_case_and_compliance(**kwargs):
    """Create case and populate compliance fields from arbitrary arguments"""
    compliance_kwargs: dict[str, Any] = {
        key: value for key, value in kwargs.items() if key in COMPLIANCE_FIELDS
    }
    non_compliance_args: dict[str, Any] = {
        key: value for key, value in kwargs.items() if key not in COMPLIANCE_FIELDS
    }
    case: Case = Case.objects.create(**non_compliance_args)
    if compliance_kwargs:
        for key, value in compliance_kwargs.items():
            setattr(case.compliance, key, value)
        case.compliance.save()
        case.save()
    return case
