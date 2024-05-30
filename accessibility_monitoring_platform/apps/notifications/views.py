"""Views for notifications app"""

from typing import Type

from django.contrib import messages
from django.db.models import QuerySet
from django.forms.models import ModelForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView
from django.views.generic.edit import UpdateView

from ..common.utils import record_model_update_event
from .forms import ReminderForm
from .models import Notification, Task
from .utils import build_task_list


class NotificationView(ListView):
    """
    Lists all notifications for user
    """

    model = Notification
    template_name: str = "notifications/view_notifications.html"
    context_object_name: str = "notifications"

    def get_queryset(self) -> QuerySet[Notification]:
        """Get reminders for logged in user"""
        notifications: QuerySet[Notification] = Notification.objects.filter(
            user=self.request.user
        )
        if self.request.GET.get("showing", "unread") == "unread":
            return notifications.filter(read=False)
        return notifications

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notifications: QuerySet[Notification] = self.get_queryset()
        context["showing"] = self.request.GET.get("showing", "unread")
        context["unread_notifications"] = len(notifications.filter(read=False))
        return context


class NotificationMarkAsReadView(ListView):
    """
    Mark notification as read
    """

    model = Notification

    def get(self, request, pk):
        """Hides a notification"""
        notification: Notification = Notification.objects.get(pk=pk)
        if (
            notification.user.id == request.user.id  # type: ignore
        ):  # Checks whether the comment was posted by user
            notification.read = True
            notification.save()
            messages.success(request, "Notification marked as seen")
        else:
            messages.error(request, "An error occured")

        showing_flag: str = self.request.GET.get("showing", "unread")
        return HttpResponseRedirect(
            f'{reverse_lazy("notifications:notifications-list")}?showing={showing_flag}'
        )


class NotificationMarkAsUnreadView(ListView):
    """
    Marks notification as unread
    """

    model = Notification

    def get(self, request, pk):
        """Marks a notification as unread"""
        notification: Notification = Notification.objects.get(pk=pk)
        if (
            notification.user.id == request.user.id  # type: ignore
        ):  # Checks whether the comment was posted by user
            notification.read = False
            notification.save()
            messages.success(request, "Notification marked as unseen")
        else:
            messages.error(request, "An error occured")

        showing_flag: str = self.request.GET.get("showing", "unread")
        return HttpResponseRedirect(
            f'{reverse_lazy("notifications:notifications-list")}?showing={showing_flag}'
        )


class TaskListView(TemplateView):
    """
    Lists all tasks for user
    """

    template_name: str = "notifications/task_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks"] = build_task_list(user=self.request.user)
        return context


class TaskMarkAsReadView(ListView):
    """
    Mark task as read
    """

    model = Task

    def get(self, request, pk):
        """Hides a task"""
        task: Task = Task.objects.get(pk=pk)
        if (
            task.user.id == request.user.id  # type: ignore
        ):  # Checks whether the task was created by user
            task.read = True
            task.save()
            if task.type == Task.Type.REMINDER:
                messages.success(request, f"{task.case} Reminder task deleted")
            else:
                messages.success(
                    request,
                    f"{task.case} {task.get_type_display()} task marked as read",
                )
        else:
            messages.error(request, "An error occured")

        return HttpResponseRedirect(reverse_lazy("notifications:task-list"))


class ReminderTaskUpdateView(UpdateView):
    """
    View to update reminder
    """

    model: Type[Task] = Task
    context_object_name: str = "task"
    form_class: Type[ReminderForm] = ReminderForm
    success_url: str = reverse_lazy("notifications:task-list")

    def form_valid(self, form: ModelForm) -> HttpResponseRedirect:
        """Add event on change of task"""
        if form.changed_data or "delete" in self.request.POST:
            self.object: Task = form.save(commit=False)
            if "delete" in self.request.POST:
                self.object.read = True
            record_model_update_event(user=self.request.user, model_object=self.object)
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["case"] = self.object.case
        return context
