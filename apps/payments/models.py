import uuid
from django.db import models
from core.models import Organization, TimeStampedModel
from invoices.models import Invoice
from banking.models import BankAccount
from core.models import User

class Payment(TimeStampedModel):
    """
    پرداخت به فاکتور یا دریافت از مشتری
    """
    PAYMENT_METHODS = [
        ("cash", "نقدی"),
        ("bank_transfer", "انتقال بانکی"),
        ("check", "چک"),
        ("other", "سایر"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="payments")
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, related_name="payments")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    paid_at = models.DateField()
    from_bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="outgoing_payments",
        help_text="حساب بانکی پرداخت کننده"
    )
    to_bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incoming_payments",
        help_text="حساب بانکی دریافت کننده"
    )
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default="cash")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"
        ordering = ("-paid_at",)
        indexes = [
            models.Index(fields=["organization", "paid_at"]),
        ]

    def __str__(self):
        return f"{self.invoice or 'No Invoice'} - {self.amount} {self.method}"

    def save(self, *args, **kwargs):
        """
        به روز رسانی فاکتور و لجر هنگام ثبت پرداخت
        """
        super().save(*args, **kwargs)
        # بروزرسانی وضعیت فاکتور
        if self.invoice:
            total_paid = sum(p.amount for p in self.invoice.payments.all())
            if total_paid >= self.invoice.total:
                self.invoice.status = "paid"
            elif total_paid > 0:
                self.invoice.status = "sent"
            else:
                self.invoice.status = "draft"
            self.invoice.save()
        # TODO: اضافه کردن اتوماتیک ژورنال در journals و ledger
