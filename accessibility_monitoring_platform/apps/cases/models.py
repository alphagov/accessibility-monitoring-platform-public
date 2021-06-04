"""
Models - cases
"""
from django.db import models
from django.db.models.deletion import CASCADE
from django.urls import reverse
from django.utils import timezone

STATUS_CHOICES = [
    ("new-case", "New case"),
    ("test-in-progress", "Test in progress"),
    ("report-in-progress", "Report in progress"),
    ("awaiting-response", "Awaiting response to report"),
    ("12w-due", "12 Week review due"),
    ("12w-sent", "12 Week review sent"),
    ("escalated", "Case sent to supporting bodies"),
    ("complete", "Complete"),
    ("archived", "Archived"),
    ("not-a-psb", "Not a public sector body"),
]

TEST_TYPE_CHOICES = [
    ("simple", "Simple"),
    ("detailed", "Detailed"),
]

WEBSITE_TYPE_CHOICES = [
    ("public", "Public website"),
    ("int-extranet", "Intranet/Extranet"),
    ("other", "Other"),
    ("unknown", "Unknown"),
]

CASE_ORIGIN_CHOICES = [
    ("org", "Organisation"),
    ("list", "Website list"),
    ("complaint", "Complaint"),
]

TEST_STATUS_CHOICES = [
    ("complete", "Complete"),
    ("in-progress", "In progress"),
    ("not-started", "Not started"),
]


class Case(models.Model):
    """
    Model for Case
    """

    created = models.DateTimeField()
    status = models.CharField(max_length=200, choices=STATUS_CHOICES)
    auditor = models.CharField(max_length=200)
    test_type = models.CharField(
        max_length=10, choices=TEST_TYPE_CHOICES, default="simple"
    )
    home_page_url = models.TextField(default="")
    domain = models.TextField(default="")
    application = models.CharField(max_length=200, default="N/A")
    organisation_name = models.TextField(default="")
    website_type = models.CharField(
        max_length=100, choices=WEBSITE_TYPE_CHOICES, default="public"
    )
    sector = models.CharField(max_length=200, default="Sector")
    region = models.CharField(max_length=200, default="London")
    case_origin = models.CharField(
        max_length=200, choices=CASE_ORIGIN_CHOICES, default="org"
    )
    zendesk_url = models.CharField(max_length=200, default="")
    trello_url = models.CharField(max_length=200, default="")
    notes = models.TextField(default="")
    is_public_sector_body = models.BooleanField(default=True)
    test_results_url = models.CharField(max_length=200, default="")
    test_status = models.CharField(
        max_length=200, choices=TEST_STATUS_CHOICES, default="not-started"
    )
    is_website_compliant = models.BooleanField(default=False)
    test_notes = models.TextField(default="")

    simplified_test_filename = models.CharField(max_length=200)
    created_by = models.CharField(max_length=200)

    def __str__(self):
        return str(f"#{self.id} {self.organisation_name}")

    def get_absolute_url(self):
        return reverse("cases:case-detail", kwargs={"pk": self.pk})


class Contact(models.Model):
    """
    Model for cases Contact
    """

    case = models.ForeignKey(Case, on_delete=CASCADE)
    first_name = models.CharField(max_length=200, default="")
    last_name = models.CharField(max_length=200, default="")
    job_title = models.CharField(max_length=200, default="")
    detail = models.CharField(max_length=200, default="")
    preferred = models.BooleanField(default=False)
    notes = models.TextField(default="")
    created = models.DateTimeField()
    created_by = models.CharField(max_length=200)
    archived = models.BooleanField(default=False)

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return str(f"Case #{self.case.id}: {self.job_title} {self.name}")

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        super().save(*args, **kwargs)
