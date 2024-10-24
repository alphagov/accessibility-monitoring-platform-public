"""
URLS for dashboard
"""

from django.contrib.auth.decorators import login_required
from django.urls import path
from django.urls.resolvers import URLPattern

from .views.base import (
    StatementCheckCreateView,
    StatementCheckListView,
    StatementCheckUpdateView,
    WcagDefinitionCreateView,
    WcagDefinitionListView,
    WcagDefinitionUpdateView,
    create_audit,
    restore_page,
)
from .views.equality_body import (
    RetestComparisonUpdateView,
    RetestComplianceUpdateView,
    RetestDisproportionateBurdenUpdateView,
    RetestMetadataUpdateView,
    RetestPageChecksFormView,
    RetestStatementComplianceFormView,
    RetestStatementCustomFormView,
    RetestStatementDecisionUpdateView,
    RetestStatementFeedbackFormView,
    RetestStatementNonAccessibleFormView,
    RetestStatementOverviewFormView,
    RetestStatementPageFormsetUpdateView,
    RetestStatementPreparationFormView,
    RetestStatementResultsUpdateView,
    RetestStatementWebsiteFormView,
    create_equality_body_retest,
    mark_retest_as_deleted,
)
from .views.initial import (
    AuditCaseComplianceStatementInitialUpdateView,
    AuditCaseComplianceWebsiteInitialUpdateView,
    AuditMetadataUpdateView,
    AuditPageChecksFormView,
    AuditPagesUpdateView,
    AuditReportOptionsUpdateView,
    AuditStatement1UpdateView,
    AuditStatement2UpdateView,
    AuditStatementComplianceFormView,
    AuditStatementCustomFormsetView,
    AuditStatementFeedbackFormView,
    AuditStatementNonAccessibleFormView,
    AuditStatementOverviewFormView,
    AuditStatementPreparationFormView,
    AuditStatementSummaryUpdateView,
    AuditStatementWebsiteFormView,
    AuditWcagSummaryUpdateView,
    InitialDisproportionateBurdenUpdateView,
    InitialStatementPageFormsetUpdateView,
    clear_published_report_data_updated_time,
)
from .views.twelve_week import (
    AuditRetestCaseComplianceStatement12WeekUpdateView,
    AuditRetestCaseComplianceWebsite12WeekUpdateView,
    AuditRetestMetadataUpdateView,
    AuditRetestPageChecksFormView,
    AuditRetestPagesView,
    AuditRetestStatement1UpdateView,
    AuditRetestStatement2UpdateView,
    AuditRetestStatementComplianceFormView,
    AuditRetestStatementCustomFormView,
    AuditRetestStatementFeedbackFormView,
    AuditRetestStatementNonAccessibleFormView,
    AuditRetestStatementOverviewFormView,
    AuditRetestStatementPreparationFormView,
    AuditRetestStatementSummaryUpdateView,
    AuditRetestStatementWebsiteFormView,
    AuditRetestWcagSummaryUpdateView,
    TwelveWeekDisproportionateBurdenUpdateView,
    TwelveWeekStatementPageFormsetUpdateView,
    start_retest,
)

app_name: str = "audits"
urlpatterns: list[URLPattern] = [
    path(
        "create-for-case/<int:case_id>/",
        login_required(create_audit),
        name="audit-create",
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
        login_required(AuditCaseComplianceWebsiteInitialUpdateView.as_view()),
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
        "<int:pk>/edit-statement-pages/",
        login_required(InitialStatementPageFormsetUpdateView.as_view()),
        name="edit-statement-pages",
    ),
    path(
        "<int:pk>/edit-statement-overview/",
        login_required(AuditStatementOverviewFormView.as_view()),
        name="edit-statement-overview",
    ),
    path(
        "<int:pk>/edit-statement-website/",
        login_required(AuditStatementWebsiteFormView.as_view()),
        name="edit-statement-website",
    ),
    path(
        "<int:pk>/edit-statement-compliance/",
        login_required(AuditStatementComplianceFormView.as_view()),
        name="edit-statement-compliance",
    ),
    path(
        "<int:pk>/edit-statement-non-accessible/",
        login_required(AuditStatementNonAccessibleFormView.as_view()),
        name="edit-statement-non-accessible",
    ),
    path(
        "<int:pk>/edit-statement-preparation/",
        login_required(AuditStatementPreparationFormView.as_view()),
        name="edit-statement-preparation",
    ),
    path(
        "<int:pk>/edit-statement-feedback/",
        login_required(AuditStatementFeedbackFormView.as_view()),
        name="edit-statement-feedback",
    ),
    path(
        "<int:pk>/edit-statement-custom/",
        login_required(AuditStatementCustomFormsetView.as_view()),
        name="edit-statement-custom",
    ),
    path(
        "<int:pk>/edit-initial-disproportionate-burden/",
        login_required(InitialDisproportionateBurdenUpdateView.as_view()),
        name="edit-initial-disproportionate-burden",
    ),
    path(
        "<int:pk>/edit-statement-decision/",
        login_required(AuditCaseComplianceStatementInitialUpdateView.as_view()),
        name="edit-statement-decision",
    ),
    path(
        "<int:pk>/edit-audit-wcag-summary/",
        login_required(AuditWcagSummaryUpdateView.as_view()),
        name="edit-audit-wcag-summary",
    ),
    path(
        "<int:pk>/edit-audit-statement-summary/",
        login_required(AuditStatementSummaryUpdateView.as_view()),
        name="edit-audit-statement-summary",
    ),
    path(
        "<int:pk>/edit-audit-report-options/",
        login_required(AuditReportOptionsUpdateView.as_view()),
        name="edit-audit-report-options",
    ),
    path(
        "<int:pk>/audit-retest-start/",
        login_required(start_retest),
        name="audit-retest-start",
    ),
    path(
        "<int:pk>/delete-retest/",
        login_required(mark_retest_as_deleted),
        name="delete-retest",
    ),
    path(
        "<int:pk>/edit-audit-retest-metadata/",
        login_required(AuditRetestMetadataUpdateView.as_view()),
        name="edit-audit-retest-metadata",
    ),
    path(
        "<int:pk>/edit-audit-retest-pages/",
        login_required(AuditRetestPagesView.as_view()),
        name="edit-audit-retest-pages",
    ),
    path(
        "pages/<int:pk>/edit-audit-retest-page-checks/",
        login_required(AuditRetestPageChecksFormView.as_view()),
        name="edit-audit-retest-page-checks",
    ),
    path(
        "<int:pk>/edit-retest-website-decision/",
        login_required(AuditRetestCaseComplianceWebsite12WeekUpdateView.as_view()),
        name="edit-audit-retest-website-decision",
    ),
    path(
        "<int:pk>/edit-retest-wcag-summary/",
        login_required(AuditRetestWcagSummaryUpdateView.as_view()),
        name="edit-audit-retest-wcag-summary",
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
        "<int:pk>/edit-audit-retest-statement-pages/",
        login_required(TwelveWeekStatementPageFormsetUpdateView.as_view()),
        name="edit-audit-retest-statement-pages",
    ),
    path(
        "<int:pk>/edit-retest-statement-overview/",
        login_required(AuditRetestStatementOverviewFormView.as_view()),
        name="edit-retest-statement-overview",
    ),
    path(
        "<int:pk>/edit-retest-statement-website/",
        login_required(AuditRetestStatementWebsiteFormView.as_view()),
        name="edit-retest-statement-website",
    ),
    path(
        "<int:pk>/edit-retest-statement-compliance/",
        login_required(AuditRetestStatementComplianceFormView.as_view()),
        name="edit-retest-statement-compliance",
    ),
    path(
        "<int:pk>/edit-retest-statement-non-accessible/",
        login_required(AuditRetestStatementNonAccessibleFormView.as_view()),
        name="edit-retest-statement-non-accessible",
    ),
    path(
        "<int:pk>/edit-retest-statement-preparation/",
        login_required(AuditRetestStatementPreparationFormView.as_view()),
        name="edit-retest-statement-preparation",
    ),
    path(
        "<int:pk>/edit-retest-statement-feedback/",
        login_required(AuditRetestStatementFeedbackFormView.as_view()),
        name="edit-retest-statement-feedback",
    ),
    path(
        "<int:pk>/edit-retest-statement-custom/",
        login_required(AuditRetestStatementCustomFormView.as_view()),
        name="edit-retest-statement-custom",
    ),
    path(
        "<int:pk>/edit-twelve-week-disproportionate-burden/",
        login_required(TwelveWeekDisproportionateBurdenUpdateView.as_view()),
        name="edit-twelve-week-disproportionate-burden",
    ),
    path(
        "<int:pk>/edit-audit-retest-statement-decision/",
        login_required(AuditRetestCaseComplianceStatement12WeekUpdateView.as_view()),
        name="edit-audit-retest-statement-decision",
    ),
    path(
        "<int:pk>/edit-retest-statement-summary/",
        login_required(AuditRetestStatementSummaryUpdateView.as_view()),
        name="edit-audit-retest-statement-summary",
    ),
    path(
        "wcag-definition-list/",
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
        "<int:pk>/clear-outdated-published-report-warning/",
        login_required(clear_published_report_data_updated_time),
        name="clear-outdated-published-report-warning",
    ),
    path(
        "statement-check-list/",
        login_required(StatementCheckListView.as_view()),
        name="statement-check-list",
    ),
    path(
        "statement-check-create/",
        login_required(StatementCheckCreateView.as_view()),
        name="statement-check-create",
    ),
    path(
        "<int:pk>/edit-statement-check/",
        login_required(StatementCheckUpdateView.as_view()),
        name="statement-check-update",
    ),
    path(
        "create-equality-body-retest/<int:case_id>/",
        login_required(create_equality_body_retest),
        name="create-equality-body-retest",
    ),
    path(
        "retests/<int:pk>/retest-metadata-update/",
        login_required(RetestMetadataUpdateView.as_view()),
        name="retest-metadata-update",
    ),
    path(
        "retest-pages/<int:pk>/retest-page-checks/",
        login_required(RetestPageChecksFormView.as_view()),
        name="edit-retest-page-checks",
    ),
    path(
        "retests/<int:pk>/retest-comparison-update/",
        login_required(RetestComparisonUpdateView.as_view()),
        name="retest-comparison-update",
    ),
    path(
        "retests/<int:pk>/retest-compliance-update/",
        login_required(RetestComplianceUpdateView.as_view()),
        name="retest-compliance-update",
    ),
    path(
        "retests/<int:pk>/edit-equality-body-statement-pages/",
        login_required(RetestStatementPageFormsetUpdateView.as_view()),
        name="edit-equality-body-statement-pages",
    ),
    path(
        "retests/<int:pk>/edit-equality-body-statement-overview/",
        login_required(RetestStatementOverviewFormView.as_view()),
        name="edit-equality-body-statement-overview",
    ),
    path(
        "retests/<int:pk>/edit-equality-body-statement-website/",
        login_required(RetestStatementWebsiteFormView.as_view()),
        name="edit-equality-body-statement-website",
    ),
    path(
        "retests/<int:pk>/edit-equality-body-statement-compliance/",
        login_required(RetestStatementComplianceFormView.as_view()),
        name="edit-equality-body-statement-compliance",
    ),
    path(
        "retests/<int:pk>/edit-equality-body-statement-non-accessible/",
        login_required(RetestStatementNonAccessibleFormView.as_view()),
        name="edit-equality-body-statement-non-accessible",
    ),
    path(
        "retests/<int:pk>/edit-equality-body-statement-preparation/",
        login_required(RetestStatementPreparationFormView.as_view()),
        name="edit-equality-body-statement-preparation",
    ),
    path(
        "retests/<int:pk>/edit-equality-body-statement-feedback/",
        login_required(RetestStatementFeedbackFormView.as_view()),
        name="edit-equality-body-statement-feedback",
    ),
    path(
        "retests/<int:pk>/edit-equality-body-statement-custom/",
        login_required(RetestStatementCustomFormView.as_view()),
        name="edit-equality-body-statement-custom",
    ),
    path(
        "retests/<int:pk>/edit-equality-body-disproportionate-burden/",
        login_required(RetestDisproportionateBurdenUpdateView.as_view()),
        name="edit-equality-body-disproportionate-burden",
    ),
    path(
        "retests/<int:pk>/edit-equality-body-statement-results/",
        login_required(RetestStatementResultsUpdateView.as_view()),
        name="edit-equality-body-statement-results",
    ),
    path(
        "retests/<int:pk>/edit-equality-body-statement-decision/",
        login_required(RetestStatementDecisionUpdateView.as_view()),
        name="edit-equality-body-statement-decision",
    ),
]
