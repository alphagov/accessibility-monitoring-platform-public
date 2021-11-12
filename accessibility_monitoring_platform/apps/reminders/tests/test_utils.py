"""
Test - reminders utility functions
"""
import pytest
from datetime import date

from django.contrib.auth.models import User

from ...cases.models import Case
from ..models import Reminder
from ..utils import get_number_of_reminders_for_user

REMINDER_DESCRIPTION = "Reminder"


@pytest.mark.django_db
def test_user_has_no_reminders():
    """User has no reminders"""
    user: User = User.objects.create()
    assert get_number_of_reminders_for_user(user) == 0


@pytest.mark.django_db
def test_user_has_reminder_due_today():
    """User has a reminder due today"""
    user: User = User.objects.create()
    case = Case.objects.create()
    Reminder.objects.create(
        due_date=date.today(),
        user=user,
        case=case,
        description=REMINDER_DESCRIPTION,
    )
    assert get_number_of_reminders_for_user(user) == 1


@pytest.mark.django_db
def test_user_has_reminder_overdue():
    """User has an overdue reminder"""
    user: User = User.objects.create()
    case = Case.objects.create()
    Reminder.objects.create(
        due_date=date(2020, 1, 1),
        user=user,
        case=case,
        description=REMINDER_DESCRIPTION,
    )
    assert get_number_of_reminders_for_user(user) == 1


@pytest.mark.django_db
def test_user_has_due_and_overdue_reminders():
    """User has reminders due today and in the past"""
    user: User = User.objects.create()
    case = Case.objects.create()
    Reminder.objects.create(
        due_date=date(2020, 1, 1),
        user=user,
        case=case,
        description=REMINDER_DESCRIPTION,
    )
    Reminder.objects.create(
        due_date=date(2020, 1, 1),
        user=user,
        case=case,
        description=REMINDER_DESCRIPTION,
    )
    assert get_number_of_reminders_for_user(user) == 2


@pytest.mark.django_db
def test_deleted_reminders_not_counted():
    """User has deleted reminders which are not counted"""
    user: User = User.objects.create()
    case = Case.objects.create()
    Reminder.objects.create(
        is_deleted=True,
        due_date=date(2020, 1, 1),
        user=user,
        case=case,
        description=REMINDER_DESCRIPTION,
    )
    Reminder.objects.create(
        is_deleted=True,
        due_date=date(2020, 1, 1),
        user=user,
        case=case,
        description=REMINDER_DESCRIPTION,
    )
    assert get_number_of_reminders_for_user(user) == 0
