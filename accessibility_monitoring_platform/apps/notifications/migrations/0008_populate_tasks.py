# Generated by Django 5.0.4 on 2024-05-29 08:19
from typing import List

from django.db import migrations


def populate_notification_tasks(apps, schema_editor):  # pylint: disable=unused-argument
    Case = apps.get_model("cases", "Case")
    Task = apps.get_model("notifications", "Task")

    Notification = apps.get_model("notifications", "Notification")
    for notification in Notification.objects.all().order_by("id"):
        path_elements: List[str] = notification.path.split("/")

        if path_elements[1] == "cases":
            case: Case = Case.objects.get(id=int(path_elements[2]))
        else:
            print(f"Not a case {notification.path}")
            case = None

        if path_elements[3] in ["edit-qa-report-approved", "edit-report-approved"]:
            type = "report-approved"
        elif path_elements[3] == "edit-qa-comments":
            type = "qa-comment"
        else:
            print(f"Unknown notification type {notification.path}")

        Task.objects.create(
            type=type,
            date=notification.created_date.date(),
            case=case,
            user=notification.user,
            read=notification.read,
            description=notification.body,
        )

    Reminder = apps.get_model("reminders", "Reminder")
    for reminder in Reminder.objects.all().order_by("id"):
        Task.objects.create(
            type="reminder",
            date=reminder.due_date,
            case=reminder.case,
            user=reminder.case.auditor,
            read=reminder.is_deleted,
            description=reminder.description,
        )


def reverse_code(apps, schema_editor):  # pylint: disable=unused-argument
    Task = apps.get_model("notifications", "Task")
    Task.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0007_task"),
        ("reminders", "0004_reminder_updated"),
    ]

    operations = [
        migrations.RunPython(populate_notification_tasks, reverse_code=reverse_code),
    ]
