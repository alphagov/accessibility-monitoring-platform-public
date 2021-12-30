"""
Views for cases app
"""
from datetime import date, timedelta
from functools import partial
from typing import Any, Callable, Dict, List, Type
import urllib

from django.contrib import messages
from django.db.models import Q
from django.db.models.query import QuerySet
from django.forms.models import ModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from ..notifications.utils import read_notification

from ..common.typing import IntOrNone
from ..common.utils import (  # type: ignore
    format_date,
    download_as_csv,
    extract_domain_from_url,
    get_field_names_for_export,
    get_id_from_button_name,
    record_model_update_event,
    record_model_create_event,
)
from .models import Case, Contact, REPORT_APPROVED_STATUS_APPROVED
from .forms import (
    CaseCreateForm,
    CaseDetailUpdateForm,
    CaseContactFormset,
    CaseContactFormsetOneExtra,
    CaseContactsUpdateForm,
    CaseSearchForm,
    CaseTestResultsUpdateForm,
    CaseReportDetailsUpdateForm,
    CaseQAProcessUpdateForm,
    CaseReportCorrespondenceUpdateForm,
    CaseReportFollowupDueDatesUpdateForm,
    CaseDeleteForm,
    CaseNoPSBContactUpdateForm,
    CaseTwelveWeekCorrespondenceUpdateForm,
    CaseTwelveWeekCorrespondenceDueDatesUpdateForm,
    CaseFinalDecisionUpdateForm,
    CaseEnforcementBodyCorrespondenceUpdateForm,
    CaseSuspendForm,
)
from .utils import (
    CaseFieldLabelAndValue,
    extract_labels_and_values,
    get_sent_date,
    download_ehrc_cases,
    filter_cases,
)

ONE_WEEK_IN_DAYS = 7
FOUR_WEEKS_IN_DAYS = 4 * ONE_WEEK_IN_DAYS
TWELVE_WEEKS_IN_DAYS = 12 * ONE_WEEK_IN_DAYS


def find_duplicate_cases(url: str, organisation_name: str = "") -> QuerySet[Case]:
    """Look for cases with matching domain or organisation name"""
    domain: str = extract_domain_from_url(url)
    if organisation_name:
        return Case.objects.filter(
            Q(organisation_name__icontains=organisation_name) | Q(domain=domain)
        )
    return Case.objects.filter(domain=domain)


def calculate_report_followup_dates(case: Case, report_sent_date: date) -> Case:
    """Calculate followup dates based on a report sent date"""
    if report_sent_date is None:
        case.report_followup_week_1_due_date = None
        case.report_followup_week_4_due_date = None
        case.report_followup_week_12_due_date = None
    else:
        case.report_followup_week_1_due_date = report_sent_date + timedelta(
            days=ONE_WEEK_IN_DAYS
        )
        case.report_followup_week_4_due_date = report_sent_date + timedelta(
            days=FOUR_WEEKS_IN_DAYS
        )
        case.report_followup_week_12_due_date = report_sent_date + timedelta(
            days=TWELVE_WEEKS_IN_DAYS
        )
    return case


def calculate_twelve_week_chaser_dates(
    case: Case, twelve_week_update_requested_date: date
) -> Case:
    """Calculate chaser dates based on a twelve week update requested date"""
    if twelve_week_update_requested_date is None:
        case.twelve_week_1_week_chaser_due_date = None
        case.twelve_week_4_week_chaser_due_date = None
    else:
        case.twelve_week_1_week_chaser_due_date = (
            twelve_week_update_requested_date + timedelta(days=ONE_WEEK_IN_DAYS)
        )
        case.twelve_week_4_week_chaser_due_date = (
            twelve_week_update_requested_date + timedelta(days=FOUR_WEEKS_IN_DAYS)
        )
    return case


def format_due_date_help_text(due_date: date) -> str:
    """Format date and prefix with 'Due' if present"""
    if due_date is None:
        return "None"
    return f"Due {format_date(due_date)}"


class CaseDetailView(DetailView):
    """
    View of details of a single case
    """

    model: Type[Case] = Case
    context_object_name: str = "case"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add undeleted contacts to context"""
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        context["contacts"] = self.object.contact_set.filter(is_deleted=False)  # type: ignore
        case_details_prefix: List[CaseFieldLabelAndValue] = [
            CaseFieldLabelAndValue(
                label="Date created",
                value=self.object.created,  # type: ignore
                type=CaseFieldLabelAndValue.DATE_TYPE,
            ),
            CaseFieldLabelAndValue(
                label="Status", value=self.object.get_status_display()  # type: ignore
            ),
        ]

        get_rows: Callable = partial(extract_labels_and_values, case=self.object)  # type: ignore

        qa_process_rows: List[CaseFieldLabelAndValue] = get_rows(
            form=CaseQAProcessUpdateForm()
        )

        context["case_details_rows"] = case_details_prefix + get_rows(
            form=CaseDetailUpdateForm()
        )
        context["testing_details_rows"] = get_rows(form=CaseTestResultsUpdateForm())
        context["report_details_rows"] = get_rows(form=CaseReportDetailsUpdateForm())
        context["qa_process_rows"] = qa_process_rows
        context["final_decision_rows"] = get_rows(form=CaseFinalDecisionUpdateForm())
        context["enforcement_body_correspondence_rows"] = get_rows(
            form=CaseEnforcementBodyCorrespondenceUpdateForm()
        )
        return context


class CaseListView(ListView):
    """
    View of list of cases
    """

    model: Type[Case] = Case
    context_object_name: str = "cases"
    paginate_by: int = 10

    def get(self, request, *args, **kwargs):
        """Populate filter form"""
        if self.request.GET:
            self.form: CaseSearchForm = CaseSearchForm(self.request.GET)
            self.form.is_valid()
        else:
            self.form = CaseSearchForm()
        return super().get(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Case]:
        """Add filters to queryset"""
        if self.form.errors:
            return Case.objects.none()

        return filter_cases(self.form)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add field values into context"""
        context: Dict[str, Any] = super().get_context_data(**kwargs)

        get_without_page: Dict[str, str] = {
            key: value for (key, value) in self.request.GET.items() if key != "page"
        }

        context["form"] = self.form
        context["url_parameters"] = urllib.parse.urlencode(get_without_page)  # type: ignore
        return context


class CaseCreateView(CreateView):
    """
    View to create a case
    """

    model: Type[Case] = Case
    form_class: Type[CaseCreateForm] = CaseCreateForm
    context_object_name: str = "case"
    template_name: str = "cases/forms/create.html"

    def form_valid(self, form: ModelForm):
        """Process contents of valid form"""
        if "allow_duplicate_cases" in self.request.GET:
            case: Case = form.save(commit=False)
            case.created_by = self.request.user
            return super().form_valid(form)

        context: Dict[str, Any] = self.get_context_data()
        duplicate_cases: QuerySet[Case] = find_duplicate_cases(
            url=form.cleaned_data.get("home_page_url", ""),
            organisation_name=form.cleaned_data.get("organisation_name", ""),
        ).order_by("created")

        if duplicate_cases:
            context["duplicate_cases"] = duplicate_cases
            context["new_case"] = form.save(commit=False)
            return self.render_to_response(context)

        case: Case = form.save(commit=False)
        case.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Detect the submit button used and act accordingly"""
        record_model_create_event(user=self.request.user, model_object=self.object)  # type: ignore
        if "save_continue_case" in self.request.POST:
            url = reverse("cases:edit-case-details", kwargs={"pk": self.object.id})  # type: ignore
        elif "save_new_case" in self.request.POST:
            url = reverse("cases:case-create")
        elif "save_exit" in self.request.POST:
            url = reverse("cases:case-list")
        else:
            url = reverse(
                "cases:edit-contact-details", kwargs={"pk": self.object.id}  # type: ignore
            )
        return url


class CaseUpdateView(UpdateView):
    """
    View to update case
    """

    model: Type[Case] = Case
    context_object_name: str = "case"

    def form_valid(self, form: ModelForm) -> HttpResponseRedirect:
        """Add message on change of case"""
        if form.changed_data:
            self.object: Case = form.save(commit=False)
            record_model_update_event(user=self.request.user, model_object=self.object)  # type: ignore
            old_case: Case = Case.objects.get(pk=self.object.id)  # type: ignore

            if (
                old_case.report_approved_status != self.object.report_approved_status
                and self.object.report_approved_status
                == REPORT_APPROVED_STATUS_APPROVED
            ):
                self.object.reviewer = self.request.user

            if "home_page_url" in form.changed_data:
                self.object.domain = extract_domain_from_url(self.object.home_page_url)

            self.object.save()

            if old_case.status != self.object.status:
                messages.add_message(
                    self.request,
                    messages.INFO,
                    f"Status changed from '{old_case.get_status_display()}'"  # type: ignore
                    f" to '{self.object.get_status_display()}'",  # type: ignore
                )
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        """Remain on current page on save"""
        return self.request.path


class CaseDetailUpdateView(CaseUpdateView):
    """
    View to update case details
    """

    form_class: Type[CaseDetailUpdateForm] = CaseDetailUpdateForm
    template_name: str = "cases/forms/details.html"


class CaseTestResultsUpdateView(CaseUpdateView):
    """
    View to update case test results
    """

    form_class: Type[CaseTestResultsUpdateForm] = CaseTestResultsUpdateForm
    template_name: str = "cases/forms/test_results.html"


class CaseReportDetailsUpdateView(CaseUpdateView):
    """
    View to update case report details
    """

    model: Type[Case] = Case
    form_class: Type[CaseReportDetailsUpdateForm] = CaseReportDetailsUpdateForm
    template_name: str = "cases/forms/report_details.html"

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add undeleted contacts to context"""
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        read_notification(self.request)
        return context


class CaseQAProcessUpdateView(CaseUpdateView):
    """
    View to update QA process
    """

    form_class: Type[CaseQAProcessUpdateForm] = CaseQAProcessUpdateForm
    template_name: str = "cases/forms/qa_process.html"


class CaseContactFormsetUpdateView(CaseUpdateView):
    """
    View to update case contacts
    """

    form_class: Type[CaseContactsUpdateForm] = CaseContactsUpdateForm
    template_name: str = "cases/forms/contact_formset.html"

    def get_context_data(self, **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Get context data for template rendering"""
        context: Dict[str, Any] = super().get_context_data(**kwargs)
        if self.request.POST:
            contacts_formset = CaseContactFormset(self.request.POST)
        else:
            contacts: QuerySet[Contact] = self.object.contact_set.filter(  # type: ignore
                is_deleted=False
            )
            if "add_extra" in self.request.GET:
                contacts_formset = CaseContactFormsetOneExtra(queryset=contacts)
            else:
                contacts_formset = CaseContactFormset(queryset=contacts)
        context["contacts_formset"] = contacts_formset
        return context

    def form_valid(self, form: ModelForm):
        """Process contents of valid form"""
        context: Dict[str, Any] = self.get_context_data()
        contact_formset = context["contacts_formset"]
        case: Case = form.save()
        if contact_formset.is_valid():
            contacts: List[Contact] = contact_formset.save(commit=False)
            for contact in contacts:
                if not contact.case_id:  # type: ignore
                    contact.case = case
                    contact.save()
                    record_model_create_event(user=self.request.user, model_object=contact)  # type: ignore
                else:
                    record_model_update_event(user=self.request.user, model_object=contact)  # type: ignore
                    contact.save()
        contact_id_to_delete: IntOrNone = get_id_from_button_name(
            button_name_prefix="remove_contact_",
            querydict=self.request.POST,
        )
        if contact_id_to_delete is not None:
            contact_to_delete: Contact = Contact.objects.get(id=contact_id_to_delete)
            contact_to_delete.is_deleted = True
            contact_to_delete.save()
            record_model_update_event(user=self.request.user, model_object=contact_to_delete)  # type: ignore
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Detect the submit button used and act accordingly"""
        case_pk: Dict[str, int] = {"pk": self.object.id}  # type: ignore
        if "save" in self.request.POST:
            url: str = reverse("cases:edit-contact-details", kwargs=case_pk)
        elif "add_contact" in self.request.POST:
            url: str = f"{reverse('cases:edit-contact-details', kwargs=case_pk)}?add_extra=true"
        else:
            contact_id_to_delete: IntOrNone = get_id_from_button_name(
                "remove_contact_", self.request.POST
            )
            if contact_id_to_delete is not None:
                url: str = reverse("cases:edit-contact-details", kwargs=case_pk)
            else:
                url: str = reverse("cases:case-detail", kwargs=case_pk)
        return url


class CaseReportCorrespondenceUpdateView(CaseUpdateView):
    """
    View to update case post report details
    """

    form_class: Type[
        CaseReportCorrespondenceUpdateForm
    ] = CaseReportCorrespondenceUpdateForm
    template_name: str = "cases/forms/report_correspondence.html"

    def get_form(self):
        """Populate help text with dates"""
        form = super().get_form()
        form.fields[
            "report_followup_week_1_sent_date"
        ].help_text = format_due_date_help_text(
            form.instance.report_followup_week_1_due_date
        )
        form.fields[
            "report_followup_week_4_sent_date"
        ].help_text = format_due_date_help_text(
            form.instance.report_followup_week_4_due_date
        )
        return form

    def form_valid(self, form: CaseReportCorrespondenceUpdateForm):
        """
        Recalculate followup dates if report sent date has changed;
        Otherwise set sent dates based on followup date checkboxes.
        """
        self.object: Case = form.save(commit=False)
        case_from_db: Case = Case.objects.get(pk=self.object.id)  # type: ignore
        if "report_sent_date" in form.changed_data:
            self.object = calculate_report_followup_dates(
                case=self.object, report_sent_date=form.cleaned_data["report_sent_date"]
            )
        else:
            for sent_date_name in [
                "report_followup_week_1_sent_date",
                "report_followup_week_4_sent_date",
            ]:
                setattr(
                    self.object,
                    sent_date_name,
                    get_sent_date(form, case_from_db, sent_date_name),
                )
        return super().form_valid(form)


class CaseReportFollowupDueDatesUpdateView(CaseUpdateView):
    """
    View to update report followup due dates
    """

    form_class: Type[
        CaseReportFollowupDueDatesUpdateForm
    ] = CaseReportFollowupDueDatesUpdateForm
    template_name: str = "cases/forms/report_followup_due_dates.html"

    def get_success_url(self) -> str:
        """Work out url to redirect to on success"""
        return reverse(
            "cases:edit-report-correspondence", kwargs={"pk": self.object.id}  # type: ignore
        )


class CaseTwelveWeekCorrespondenceUpdateView(CaseUpdateView):
    """
    View to record week twelve correspondence details
    """

    form_class: Type[
        CaseTwelveWeekCorrespondenceUpdateForm
    ] = CaseTwelveWeekCorrespondenceUpdateForm
    template_name: str = "cases/forms/twelve_week_correspondence.html"

    def get_form(self):
        """Populate help text with dates"""
        form = super().get_form()
        form.fields[
            "twelve_week_1_week_chaser_sent_date"
        ].help_text = format_due_date_help_text(
            form.instance.twelve_week_1_week_chaser_due_date
        )
        form.fields[
            "twelve_week_4_week_chaser_sent_date"
        ].help_text = format_due_date_help_text(
            form.instance.twelve_week_4_week_chaser_due_date
        )
        return form

    def form_valid(self, form: CaseTwelveWeekCorrespondenceUpdateForm):
        """
        Recalculate chaser dates if twelve week update requested date has changed;
        Otherwise set sent dates based on chaser date checkboxes.
        """
        self.object: Case = form.save(commit=False)
        case_from_db: Case = Case.objects.get(pk=self.object.id)  # type: ignore
        if "twelve_week_update_requested_date" in form.changed_data:
            self.object = calculate_twelve_week_chaser_dates(
                case=self.object,
                twelve_week_update_requested_date=form.cleaned_data[
                    "twelve_week_update_requested_date"
                ],
            )
        else:
            for sent_date_name in [
                "twelve_week_1_week_chaser_sent_date",
                "twelve_week_4_week_chaser_sent_date",
            ]:
                setattr(
                    self.object,
                    sent_date_name,
                    get_sent_date(form, case_from_db, sent_date_name),  # type: ignore
                )
        return super().form_valid(form)


class CaseTwelveWeekCorrespondenceDueDatesUpdateView(CaseUpdateView):
    """
    View to update twelve week correspondence followup due dates
    """

    form_class: Type[
        CaseTwelveWeekCorrespondenceDueDatesUpdateForm
    ] = CaseTwelveWeekCorrespondenceDueDatesUpdateForm
    template_name: str = "cases/forms/twelve_week_correspondence_due_dates.html"

    def get_success_url(self) -> str:
        """Work out url to redirect to on success"""
        return reverse(
            "cases:edit-twelve-week-correspondence", kwargs={"pk": self.object.id}  # type: ignore
        )


class CaseNoPSBResponseUpdateView(CaseUpdateView):
    """
    View to set no psb contact flag
    """

    form_class: Type[CaseNoPSBContactUpdateForm] = CaseNoPSBContactUpdateForm
    template_name: str = "cases/forms/no_psb_response.html"

    def get_success_url(self) -> str:
        """Work out url to redirect to on success"""
        return reverse(
            "cases:edit-enforcement-body-correspondence",
            kwargs={"pk": self.object.id},  # type: ignore
        )


class CaseFinalDecisionUpdateView(CaseUpdateView):
    """
    View to record final decision details
    """

    form_class: Type[CaseFinalDecisionUpdateForm] = CaseFinalDecisionUpdateForm
    template_name: str = "cases/forms/final_decision.html"

    def get_form(self):
        """Populate retested_website_date help text with link to test results for this case"""
        form = super().get_form()
        if form.instance.test_results_url:
            if form.instance.test_results_url:
                form.fields["retested_website_date"].help_text = mark_safe(
                    f'The retest form can be found in the <a href="{form.instance.test_results_url}"'
                    ' class="govuk-link govuk-link--no-visited-state" target="_blank">test results</a>'
                )
        return form


class CaseEnforcementBodyCorrespondenceUpdateView(CaseUpdateView):
    """
    View to note correspondence with enforcement body
    """

    form_class: Type[
        CaseEnforcementBodyCorrespondenceUpdateForm
    ] = CaseEnforcementBodyCorrespondenceUpdateForm
    template_name: str = "cases/forms/enforcement_body_correspondence.html"


class CaseDeleteUpdateView(CaseUpdateView):
    """
    View to delete case
    """

    form_class: Type[CaseDeleteForm] = CaseDeleteForm
    template_name: str = "cases/forms/delete.html"

    def form_valid(self, form: ModelForm):
        """Process contents of valid form"""
        case: Case = form.save(commit=False)
        case.is_deleted = True
        record_model_update_event(user=self.request.user, model_object=case)  # type: ignore
        case.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self) -> str:
        """Work out url to redirect to on success"""
        return reverse("cases:case-list")


class CaseSuspendUpdateView(CaseUpdateView):
    """
    View to suspend case
    """

    form_class: Type[CaseSuspendForm] = CaseSuspendForm
    template_name: str = "cases/forms/suspend.html"

    def form_valid(self, form: ModelForm):
        """Process contents of valid form"""
        case: Case = form.save(commit=False)
        case.is_suspended = True
        case.suspend_date = date.today()
        record_model_update_event(user=self.request.user, model_object=case)  # type: ignore
        case.save()
        return HttpResponseRedirect(case.get_absolute_url())


class CaseUnsuspendUpdateView(CaseUpdateView):
    """
    View to unsuspend case
    """

    form_class: Type[CaseSuspendForm] = CaseSuspendForm
    template_name: str = "cases/forms/unsuspend.html"

    def form_valid(self, form: ModelForm):
        """Process contents of valid form"""
        case: Case = form.save(commit=False)
        case.is_suspended = False
        record_model_update_event(user=self.request.user, model_object=case)  # type: ignore
        case.save()
        return HttpResponseRedirect(case.get_absolute_url())


def export_cases(request: HttpRequest) -> HttpResponse:
    """
    View to export cases

    Args:
        request (HttpRequest): Django HttpRequest

    Returns:
        HttpResponse: Django HttpResponse
    """
    case_search_form: CaseSearchForm = CaseSearchForm(request.GET)
    case_search_form.is_valid()
    return download_as_csv(
        queryset=filter_cases(form=case_search_form),
        field_names=get_field_names_for_export(Case),
        filename="cases.csv",
        include_contact=True,
    )


def export_single_case(
    request: HttpRequest, pk: int  # pylint: disable=unused-argument
) -> HttpResponse:
    """
    View to export a single case in csv format

    Args:
        request (HttpRequest): Django HttpRequest
        pk: int

    Returns:
        HttpResponse: Django HttpResponse
    """
    return download_as_csv(
        queryset=Case.objects.filter(id=pk),
        field_names=get_field_names_for_export(Case),
        filename=f"case_#{pk}.csv",
        include_contact=True,
    )


def export_ehrc_cases(request: HttpRequest) -> HttpResponse:
    """
    View to export cases to send to an enforcement body

    Args:
        request (HttpRequest): Django HttpRequest

    Returns:
        HttpResponse: Django HttpResponse
    """
    case_search_form: CaseSearchForm = CaseSearchForm(request.GET)
    case_search_form.is_valid()
    return download_ehrc_cases(cases=filter_cases(form=case_search_form))


def restore_case(
    request: HttpRequest, pk: int  # pylint: disable=unused-argument
) -> HttpResponse:
    """
    Restore deleted case

    Args:
        request (HttpRequest): Django HttpRequest
        pk (int): Id of case to restore

    Returns:
        HttpResponse: Django HttpResponse
    """
    case: Case = get_object_or_404(Case, id=pk)
    case.is_deleted = False
    case.save()
    return redirect(reverse("cases:case-detail", kwargs={"pk": case.id}))  # type: ignore
