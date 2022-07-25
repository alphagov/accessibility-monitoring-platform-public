"""
URLS for dashboard
"""
from typing import List

from django.contrib.auth.decorators import login_required
from django.urls import path
from django.urls.resolvers import URLPattern
from .views import (
    AuditAllIssuesListView,
    AuditDetailView,
    AuditMetadataUpdateView,
    AuditPagesUpdateView,
    AuditPageChecksFormView,
    AuditWebsiteDecisionUpdateView,
    AuditStatement1UpdateView,
    AuditStatement2UpdateView,
    AuditStatementDecisionUpdateView,
    AuditSummaryUpdateView,
    AuditReportOptionsUpdateView,
    AuditReportTextUpdateView,
    AuditRetestDetailView,
    AuditRetestMetadataUpdateView,
    AuditRetestPagesUpdateView,
    AuditRetestPageChecksFormView,
    AuditRetestWebsiteDecisionUpdateView,
    AuditRetestStatement1UpdateView,
    AuditRetestStatement2UpdateView,
    AuditRetestStatementDecisionUpdateView,
    WcagDefinitionListView,
    WcagDefinitionCreateView,
    WcagDefinitionUpdateView,
    create_audit,
    delete_audit,
    restore_audit,
    delete_page,
    restore_page,
    start_retest,
    clear_report_data_updated_time,
)

app_name: str = "audits"
urlpatterns: List[URLPattern] = [
    path(
        "all-issues/",
        login_required(AuditAllIssuesListView.as_view()),
        name="audit-all-issues",
    ),
    path(
        "create-for-case/<int:case_id>/",
        login_required(create_audit),
        name="audit-create",
    ),
    path(
        "<int:pk>/detail/",
        login_required(AuditDetailView.as_view()),
        name="audit-detail",
    ),
    path(
        "<int:pk>/delete-audit/",
        login_required(delete_audit),
        name="delete-audit",
    ),
    path(
        "<int:pk>/restore-audit/",
        login_required(restore_audit),
        name="restore-audit",
    ),
    path(
        "<int:pk>/edit-audit-metadata/",
        login_required(AuditMetadataUpdateView.as_view()),
        name="edit-audit-metadata",
    ),
    path(
        "<int:pk>/edit-audit-pages/",
        login_required(AuditPagesUpdateView.as_view()),
        name="edit-audit-pages",
    ),
    path(
        "pages/<int:pk>/delete-page/",
        login_required(delete_page),
        name="delete-page",
    ),
    path(
        "pages/<int:pk>/restore-page/",
        login_required(restore_page),
        name="restore-page",
    ),
    path(
        "pages/<int:pk>/edit-audit-page-checks/",
        login_required(AuditPageChecksFormView.as_view()),
        name="edit-audit-page-checks",
    ),
    path(
        "<int:pk>/edit-website-decision/",
        login_required(AuditWebsiteDecisionUpdateView.as_view()),
        name="edit-website-decision",
    ),
    path(
        "<int:pk>/edit-audit-statement-one/",
        login_required(AuditStatement1UpdateView.as_view()),
        name="edit-audit-statement-1",
    ),
    path(
        "<int:pk>/edit-audit-statement-two/",
        login_required(AuditStatement2UpdateView.as_view()),
        name="edit-audit-statement-2",
    ),
    path(
        "<int:pk>/edit-statement-decision/",
        login_required(AuditStatementDecisionUpdateView.as_view()),
        name="edit-statement-decision",
    ),
    path(
        "<int:pk>/edit-audit-summary/",
        login_required(AuditSummaryUpdateView.as_view()),
        name="edit-audit-summary",
    ),
    path(
        "<int:pk>/edit-audit-report-options/",
        login_required(AuditReportOptionsUpdateView.as_view()),
        name="edit-audit-report-options",
    ),
    path(
        "<int:pk>/edit-audit-report-text/",
        login_required(AuditReportTextUpdateView.as_view()),
        name="edit-audit-report-text",
    ),
    path(
        "<int:pk>/audit-retest-start/",
        login_required(start_retest),
        name="audit-retest-start",
    ),
    path(
        "<int:pk>/audit-retest-detail/",
        login_required(AuditRetestDetailView.as_view()),
        name="audit-retest-detail",
    ),
    path(
        "<int:pk>/edit-audit-retest-metadata/",
        login_required(AuditRetestMetadataUpdateView.as_view()),
        name="edit-audit-retest-metadata",
    ),
    path(
        "<int:pk>/edit-audit-retest-pages/",
        login_required(AuditRetestPagesUpdateView.as_view()),
        name="edit-audit-retest-pages",
    ),
    path(
        "pages/<int:pk>/edit-audit-retest-page-checks/",
        login_required(AuditRetestPageChecksFormView.as_view()),
        name="edit-audit-retest-page-checks",
    ),
    path(
        "<int:pk>/edit-retest-website-decision/",
        login_required(AuditRetestWebsiteDecisionUpdateView.as_view()),
        name="edit-audit-retest-website-decision",
    ),
    path(
        "<int:pk>/edit-audit-retest-statement-1/",
        login_required(AuditRetestStatement1UpdateView.as_view()),
        name="edit-audit-retest-statement-1",
    ),
    path(
        "<int:pk>/edit-audit-retest-statement-2/",
        login_required(AuditRetestStatement2UpdateView.as_view()),
        name="edit-audit-retest-statement-2",
    ),
    path(
        "<int:pk>/edit-audit-retest-statement-decision/",
        login_required(AuditRetestStatementDecisionUpdateView.as_view()),
        name="edit-audit-retest-statement-decision",
    ),
    path(
        "wcag-definition-list",
        login_required(WcagDefinitionListView.as_view()),
        name="wcag-definition-list",
    ),
    path(
        "wcag-definition-create/",
        login_required(WcagDefinitionCreateView.as_view()),
        name="wcag-definition-create",
    ),
    path(
        "<int:pk>/edit-wcag-definition/",
        login_required(WcagDefinitionUpdateView.as_view()),
        name="wcag-definition-update",
    ),
    path(
        "<int:pk>/clear-outdated-report-warning/",
        login_required(clear_report_data_updated_time),
        name="clear-outdated-report-warning",
    ),
]
