import uuid
from django.db import models
from django.core.validators import MinValueValidator
from core.models import Organization
from chartofaccounts.models import Account
from accounts.models import User
from costcenters.models import CostCenter  # اگر اپ costcenters داری
from core.models import TimeStampedModel  # optional abstract model


class JournalEntry(TimeStampedModel):
    """
    سند ژورنال
    """
    STATUS_CHOICES = [
        ("draft", "پیش‌نویس"),
        ("posted", "ثبت شده"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="journal_entries"
    )
    entry_date = models.DateField()
    reference = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    class Meta:
        verbose_name = "سند ژورنال"
        verbose_name_plural = "سندهای ژورنال"
        ordering = ("-entry_date",)

    def __str__(self):
        return f"{self.entry_date} - {self.reference or self.id}"


class JournalLine(TimeStampedModel):
    """
    خطوط سند ژورنال
    """
    DC_CHOICES = [
        ("D", "بدهکار"),
        ("C", "بستانکار"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    journal_entry = models.ForeignKey(
        JournalEntry, on_delete=models.CASCADE, related_name="lines"
    )
    account = models.ForeignKey(
        Account, on_delete=models.PROTECT, related_name="journal_lines"
    )
    amount = models.DecimalField(max_digits=18, decimal_places=2, validators=[MinValueValidator(0.01)])
    dc_indicator = models.CharField(max_length=1, choices=DC_CHOICES)
    project_id = models.UUIDField(blank=True, null=True)
    cost_center = models.ForeignKey(
        CostCenter, on_delete=models.SET_NULL, null=True, blank=True, related_name="journal_lines"
    )

    class Meta:
        verbose_name = "خط ژورنال"
        verbose_name_plural = "خطوط ژورنال"
        ordering = ("journal_entry",)
        # می‌توان یک index برای سریع فچ کردن خطوط یک سند زد
        indexes = [
            models.Index(fields=["journal_entry", "account"]),
        ]

    def __str__(self):
        return f"{self.journal_entry} - {self.account} - {self.dc_indicator} {self.amount}"
