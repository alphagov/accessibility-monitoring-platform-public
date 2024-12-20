"""Models for notifications app"""

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from ..cases.models import Case
from ..common.models import Link


class Task(models.Model):
    """Django model for user-specific tasks"""

    class Type(models.TextChoices):
        QA_COMMENT = "qa-comment", "QA comment"
        REPORT_APPROVED = "report-approved", "Report approved"
        REMINDER = "reminder"
        OVERDUE = "overdue"
        POSTCASE = "postcase", "Post case"

    type = models.CharField(max_length=20, choices=Type, default=Type.REMINDER)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateField()
    case = models.ForeignKey(Case, on_delete=models.PROTECT, blank=True, null=True)
    description = models.TextField(default="")
    read = models.BooleanField(default=False)
    action = models.TextField(default="N/A")
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: list[str] = ["-id"]

    def options(self) -> list[Link]:
        options: list[Link] = []
        if self.type == Task.Type.QA_COMMENT:
            options.append(
                Link(
                    label="Go to QA comment",
                    url=reverse(
                        "cases:edit-qa-comments",
                        kwargs={"pk": self.case.id},
                    ),
                ),
            )
        elif self.type == Task.Type.REPORT_APPROVED:
            options.append(
                Link(
                    label="Go to Report approved",
                    url=reverse(
                        "cases:edit-qa-approval",
                        kwargs={"pk": self.case.id},
                    ),
                ),
            )
        elif self.type == Task.Type.REMINDER:
            if self.read is True:
                options.append(
                    Link(
                        label="Create new",
                        url=reverse(
                            "notifications:reminder-create",
                            kwargs={"case_id": self.case.id},
                        ),
                    )
                )
            else:
                options.append(
                    Link(
                        label="Edit",
                        url=reverse(
                            "notifications:edit-reminder-task",
                            kwargs={"pk": self.id},
                        ),
                    )
                )
                options.append(
                    Link(
                        label="Delete reminder",
                        url=reverse(
                            "notifications:mark-task-read",
                            kwargs={"pk": self.id},
                        ),
                    ),
                )
        if self.type in [Task.Type.QA_COMMENT, Task.Type.REPORT_APPROVED]:
            options.append(
                Link(
                    label="Mark as seen",
                    url=reverse(
                        "notifications:mark-task-read",
                        kwargs={"pk": self.id},
                    ),
                )
            )
            options.append(
                Link(
                    label="Mark case tasks as seen",
                    url=reverse(
                        "notifications:mark-case-comments-read",
                        kwargs={"case_id": self.case.id},
                    ),
                ),
            )
        return options


class NotificationSetting(models.Model):
    """Django model for notifications settings"""

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="notification_settings_user",
        primary_key=True,
    )
    email_notifications_enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name: str = "NotificationSetting"
        verbose_name_plural: str = "NotificationSettings"

    def __str__(self) -> str:
        return f"{self.user} - email_notifications_enabled is {self.email_notifications_enabled}"
