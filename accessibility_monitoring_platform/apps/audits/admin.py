"""
Admin for checks (called tests by the users)
"""

from django.contrib import admin

from .models import Audit, Page, CheckResult, WcagDefinition


class AuditAdmin(admin.ModelAdmin):
    """Django admin configuration for Audit model"""

    search_fields = ["case"]
    list_display = ["type", "date_of_test", "case"]


class PageAdmin(admin.ModelAdmin):
    """Django admin configuration for Page model"""

    search_fields = ["name", "url", "audit"]
    list_display = ["type", "audit", "name", "url"]


class CheckResultAdmin(admin.ModelAdmin):
    """Django admin configuration for CheckResult model"""

    search_fields = ["wcag_definition__name"]
    list_display = ["wcag_definition", "audit", "page"]


class WcagDefinitionAdmin(admin.ModelAdmin):
    """Django admin configuration for WcagDefinition model"""

    search_fields = ["name", "description"]
    list_display = ["id", "type", "sub_type", "name"]
    list_filter = ["type", "sub_type"]


admin.site.register(Audit, AuditAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(CheckResult, CheckResultAdmin)
admin.site.register(WcagDefinition, WcagDefinitionAdmin)
