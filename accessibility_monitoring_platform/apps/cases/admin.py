"""
Admin for cases
"""
from django.contrib import admin

from .models import Case, Contact


class CaseAdmin(admin.ModelAdmin):
    """Django admin configuration for Case model"""

    readonly_fields = ["created"]
    search_fields = ["organisation_name", "domain"]
    list_display = ["organisation_name", "domain", "auditor", "created"]
    list_filter = ["auditor"]


class ContactAdmin(admin.ModelAdmin):
    """Django admin configuration for Contact model"""

    search_fields = [
        "name",
        "job_title",
        "email",
        "case__organisation_name",
    ]
    list_display = ["email", "name", "job_title", "case"]
    autocomplete_fields = ["case"]


admin.site.register(Case, CaseAdmin)
admin.site.register(Contact, ContactAdmin)
