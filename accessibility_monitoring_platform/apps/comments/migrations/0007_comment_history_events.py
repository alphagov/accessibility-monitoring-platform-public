# Generated by Django 4.1.4 on 2023-02-24 08:17
from typing import Dict
import json

from django.conf import settings
from django.core import serializers
from django.db import migrations


def convert_comment_history(apps, schema_editor):  # pylint: disable=unused-argument
    """Convert comment history objects into events"""
    CommentHistory = apps.get_model("comments", "CommentHistory")
    Comment = apps.get_model("comments", "Comment")
    Event = apps.get_model("common", "Event")
    if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
        # This process goes haywire when using sqlite (e.g. setting up test env)
        comment_contenttype_id = 45
    else:
        ContentType = apps.get_model("contenttypes", "contenttype")
        comment_contenttype = ContentType.objects.get(app_label="comments", model="comment")
        comment_contenttype_id = comment_contenttype.id

    for comment_history in CommentHistory.objects.all():
        value: Dict[str, str] = {}
        old_comment = comment_history.comment
        new_comment = Comment.objects.get(id=comment_history.comment.id)

        old_comment.body = comment_history.before
        new_comment.body = comment_history.after
        value["old"] = serializers.serialize("json", [old_comment])
        value["new"] = serializers.serialize("json", [new_comment])

        event = Event.objects.create(
            created_by=comment_history.comment.user,
            content_type_id=comment_contenttype_id,
            object_id=comment_history.comment.id,
            value=json.dumps(value),
        )
        event.created = comment_history.created_date
        event.save()


def delete_comment_events(apps, schema_editor):  # pylint: disable=unused-argument
    """Delete comment events"""
    ContentType = apps.get_model("contenttypes", "contenttype")
    comment_contenttype = ContentType.objects.get(app_label="comments", model="comment")
    comment_contenttype_id = comment_contenttype.id
    Event = apps.get_model("common", "Event")

    Event.objects.filter(content_type_id=comment_contenttype_id).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("comments", "0006_alter_comment_options_remove_comment_page_and_more"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.RunPython(
            convert_comment_history, reverse_code=delete_comment_events
        ),
    ]