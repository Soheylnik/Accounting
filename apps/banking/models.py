import uuid
from django.db import models
from core.models import Organization, TimeStampedModel
from core.models import User

class BankAccount(TimeStampedModel):
    """
    حساب بانکی یک سازمان
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="bank_accounts")
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        verbose_name = "حساب بانکی"
        verbose_name_plural = "حساب‌های بانکی"
        ordering = ("bank_name", "account_number")
        unique_together = ("organization", "account_number")

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


class Reconciliation(TimeStampedModel):
    """
    تسویه حساب بانکی (Bank Reconciliation)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bank_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="reconciliations")
    start_date = models.DateField()
    end_date = models.DateField()
    statement_balance = models.DecimalField(max_digits=18, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "تسویه بانکی"
        verbose_name_plural = "تسویه‌های بانکی"
        ordering = ("-end_date",)
        indexes = [
            models.Index(fields=["bank_account", "start_date", "end_date"]),
        ]

    def __str__(self):
        return f"{self.bank_account} | {self.start_date} - {self.end_date} | Balance:{self.statement_balance}"
