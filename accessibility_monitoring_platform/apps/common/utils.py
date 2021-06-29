""" Common utility functions """
from datetime import date, datetime
import re
import csv
import pytz
from typing import (
    Any,
    Dict,
    List,
    Tuple,
)

from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpResponse
from django.http.request import QueryDict

from .typing import IntOrNone, StringOrNone

CONTACT_FIELDS = ["contact_email", "contact_notes"]


def download_as_csv(
    queryset: QuerySet, field_names: List[str], filename: str = "download.csv", include_contact: bool = False
) -> HttpResponse:
    """ Given a queryset and a list of field names, download the data in csv format """
    response: Any = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f"attachment; filename={filename}"

    writer: Any = csv.writer(response)
    if include_contact:
        writer.writerow(field_names + CONTACT_FIELDS)
    else:
        writer.writerow(field_names)

    output: List[List[str]] = []
    for item in queryset:
        row = []
        for field_name in field_names:
            item_attr = getattr(item, field_name)
            if hasattr(item_attr, "all"):
                value = ",".join([str(related_item) for related_item in item_attr.all()])
            else:
                value = item_attr
            row.append(value)

        if include_contact:
            contacts = list(item.contact_set.filter(is_archived=False))
            if contacts:
                row.append(contacts[0].detail)
                row.append(contacts[0].notes)

        output.append(row)

    writer.writerows(output)

    return response


def extract_domain_from_url(url):
    domain_match = re.search("https?://([A-Za-z_0-9.-]+).*", url)
    return domain_match.group(1) if domain_match else ""


def get_id_from_button_name(button_name_prefix: str, querydict: QueryDict) -> IntOrNone:
    """
    Given a button name in the form: prefix_[id] extract and return the id value.
    """
    key_names: Dict[str] = [
        key for key in querydict.keys() if key.startswith(button_name_prefix)
    ]
    object_id: IntOrNone = None
    if len(key_names) == 1:
        id_string: str = key_names[0].replace(button_name_prefix, "")
        object_id: IntOrNone = int(id_string) if id_string.isdigit() else None
    return object_id


def build_filters(
    cleaned_data: Dict, field_and_filter_names: List[Tuple[str, str]]
) -> Dict[str, Any]:
    """
    Given the form cleaned_data, work through a list of field and filter names
    to build up a dictionary of filters to apply in a queryset.
    """
    filters: Dict[str, Any] = {}
    for field_name, filter_name in field_and_filter_names:
        value: StringOrNone = cleaned_data.get(field_name)
        if value:
            filters[filter_name] = value
    return filters


def convert_date_to_datetime(input_date: date) -> datetime:
    """
    Python dates are not timezone-aware. This function converts a date into a timezone-aware
    datetime with a time of midnight UTC
    """
    return datetime(
        year=input_date.year,
        month=input_date.month,
        day=input_date.day,
        tzinfo=pytz.UTC,
    )


def validate_url(url):
    """
    Validate URL string entered by user
    """

    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValidationError("URL must start with http:// or https://")
