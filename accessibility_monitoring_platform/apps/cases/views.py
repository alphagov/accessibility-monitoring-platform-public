"""
Views for cases
"""
from django.views.generic.list import ListView

from .models import Case
from .forms import SearchForm


class CaseListView(ListView):
    model = Case
    paginate_by = 10

    def get_queryset(self):
        """ Add filters to queryset """
        filters = {}
        form = SearchForm(self.request.GET)
        form.is_valid()
        case_number = form.cleaned_data.get("case-number")
        if case_number:
            filters["id"] = case_number
        domain = form.cleaned_data.get("domain")
        if domain:
            filters["domain__icontains"] = domain
        organisation = form.cleaned_data.get("organisation")
        if organisation:
            filters["website_name__icontains"] = organisation
        auditor = form.cleaned_data.get("auditor")
        if auditor:
            filters["auditor"] = auditor
        filters["created__gte"] = form.start_date
        filters["created__lte"] = form.end_date
        return Case.objects.filter(**filters)

    def get_context_data(self, **kwargs):
        """ Add field values into contex """
        context = super().get_context_data(**kwargs)
        context["form"] = SearchForm(self.request.GET)
        context["case_number"] = self.request.GET.get("case-number", "")
        context["auditor"] = self.request.GET.get("auditor", "")
        return context
