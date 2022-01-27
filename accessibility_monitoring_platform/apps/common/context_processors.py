"""
Context processors
"""
from typing import Dict, Union

from ..common.models import Platform
from ..common.utils import get_platform_settings
from ..reminders.utils import get_number_of_reminders_for_user
from ..overdue.utils import get_overdue_cases
from .forms import AMPTopMenuForm


def platform_page(
    request,
) -> Dict[str, Union[AMPTopMenuForm, str, Platform, int]]:
    """
    Populate context for template rendering. Include search form for top menu,
    name of prototype, platform settings and number of reminders.
    """
    absolute_uri: str = request.build_absolute_uri()
    if (
        "localhost" in absolute_uri
        or "accessibility-monitoring-platform-production.london.cloudapps.digital"
        in absolute_uri
        or "accessibility-monitoring-platform-test.london.cloudapps.digital"
        in absolute_uri
    ):
        prototype_name: str = ""
    else:
        prototype_name: str = (
            absolute_uri.split(".")[0].replace("https://", "").replace("http://", "")
        )

    platform: Platform = get_platform_settings()

    return {
        "top_menu_form": AMPTopMenuForm(),
        "prototype_name": prototype_name,
        "platform": platform,
        "number_of_reminders": get_number_of_reminders_for_user(user=request.user),
        "number_of_overdue": len(get_overdue_cases(user_request=request.user) or []),
    }
