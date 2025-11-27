import uuid
from django.db import models
from django.conf import settings


class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    timezone = models.CharField(max_length=100, default="UTC")
    base_currency = models.CharField(max_length=10, default="USD")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class OrganizationUser(models.Model):
    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("accountant", "Accountant"),
        ("auditor", "Auditor"),
        ("viewer", "Viewer"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("organization", "user")

    def __str__(self):
        return f"{self.user} - {self.organization} ({self.role})"


class OrganizationSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.OneToOneField(
        Organization, on_delete=models.CASCADE, related_name="settings"
    )

    fiscal_year_start = models.DateField(null=True, blank=True)
    default_tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    decimal_places = models.IntegerField(default=2)
    date_format = models.CharField(max_length=20, default="YYYY-MM-DD")
    auto_post_journals = models.BooleanField(default=False)
    allow_negative_inventory = models.BooleanField(default=False)
    extra_settings = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Settings for {self.organization.name}"


class DocumentNumbering(models.Model):
    DOCUMENT_TYPES = [
        ("invoice", "Invoice"),
        ("journal", "Journal Entry"),
        ("payment", "Payment"),
        ("asset", "Fixed Asset"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="numbering_rules"
    )
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)

    prefix = models.CharField(max_length=20, blank=True, null=True)
    suffix = models.CharField(max_length=20, blank=True, null=True)

    next_number = models.PositiveIntegerField(default=1)

    reset_period = models.CharField(
        max_length=20,
        choices=[
            ("never", "Never"),
            ("yearly", "Yearly"),
            ("monthly", "Monthly"),
        ],
        default="never",
    )

    last_reset = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ("organization", "document_type")

    def __str__(self):
        return f"{self.document_type} numbering for {self.organization.name}"
