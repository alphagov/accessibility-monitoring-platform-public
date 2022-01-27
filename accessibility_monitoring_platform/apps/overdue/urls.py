"""
URLS for notifications
"""

from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import OverdueView


app_name = "overdue"
urlpatterns = [
    path(
        "overdue-list/",
        login_required(OverdueView.as_view()),
        name="overdue-list",
    ),
]
