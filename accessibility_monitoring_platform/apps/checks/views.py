"""
Views for checks app (called tests by users)
"""
from typing import Type

from django.forms.models import ModelForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .forms import CheckCreateForm
from .models import Check, EXEMPTION_DEFAULT, TYPE_DEFAULT
from ..cases.models import Case

from ..common.utils import (  # type: ignore
    record_model_update_event,
    record_model_create_event,
)

class CheckCreateView(CreateView):
    """
    View to create a check
    """

    model: Type[Check] = Check
    context_object_name: str = "check"
    form_class: Type[CheckCreateForm] = CheckCreateForm
    template_name: str = "checks/create_form.html"

    def form_valid(self, form: ModelForm):
        """Process contents of valid form"""
        check: Check = form.save(commit=False)
        check.case = Case.objects.get(pk=self.kwargs["case_id"])
        return super().form_valid(form)

    def get_form(self):
        """Initialise form fields"""
        form = super().get_form()
        form.fields["is_exemption"].initial = EXEMPTION_DEFAULT
        form.fields["type"].initial = TYPE_DEFAULT
        return form

    def get_success_url(self) -> str:
        """Detect the submit button used and act accordingly"""
        record_model_create_event(user=self.request.user, model_object=self.object)  # type: ignore
        if "save_continue" in self.request.POST:
            url = reverse_lazy(
                "checks:edit-check-metadata",
                kwargs={
                    "pk": self.object.id,  # type: ignore
                    "case_id": self.object.case.id,  # type: ignore
                },
            )
        else:
            url = reverse_lazy("cases:edit-test-results", kwargs={"pk": self.object.case.id})  # type: ignore
        return url

class CheckDetailView(DetailView):
    """
    View of details of a single check
    """

    model: Type[Check] = Check
    context_object_name: str = "check"


class CheckUpdateView(UpdateView):
    """
    View to update check
    """

    model: Type[Check] = Check
    context_object_name: str = "check"


class CheckListView(ListView):
    """
    View of list of checks
    """

    model: Type[Check] = Check
    context_object_name: str = "checks"
    paginate_by: int = 10
