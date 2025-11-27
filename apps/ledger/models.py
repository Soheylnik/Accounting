import uuid
from django.db import models
from core.models import Organization
from chartofaccounts.models import Account
from journals.models import JournalLine
from core.models import TimeStampedModel

class LedgerEntry(TimeStampedModel):
    """
    رکورد ledger: محاسبه مانده‌ها بر اساس ژورنال‌ها
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="ledger_entries")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="ledger_entries")
    date = models.DateField()
    debit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        verbose_name = "رکورد لجر"
        verbose_name_plural = "رکوردهای لجر"
        ordering = ("account", "date")
        indexes = [
            models.Index(fields=["organization", "account", "date"]),
        ]

    def __str__(self):
        return f"{self.date} - {self.account} - Debit:{self.debit} Credit:{self.credit} Balance:{self.balance}"

    def update_balance(self, previous_balance=0):
        """
        محاسبه مانده بر اساس بدهکار و بستانکار
        """
        self.balance = previous_balance + self.debit - self.credit
        self.save()
        return self.balance


class LedgerSummary(TimeStampedModel):
    """
    خلاصه حساب‌ها برای گزارش‌های Trial Balance یا Financial Reports
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="ledger_summaries")
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="ledger_summaries")
    period_start = models.DateField()
    period_end = models.DateField()
    opening_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    debit_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    credit_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    closing_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        verbose_name = "خلاصه لجر"
        verbose_name_plural = "خلاصه لجرها"
        ordering = ("account", "period_start")
        indexes = [
            models.Index(fields=["organization", "account", "period_start"]),
        ]

    def __str__(self):
        return f"{self.account} | {self.period_start} - {self.period_end} | Balance:{self.closing_balance}"
