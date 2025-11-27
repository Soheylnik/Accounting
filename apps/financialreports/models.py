import uuid
from django.db import models
from core.models import Organization
from chartofaccounts.models import Account
from ledger.models import LedgerSummary
from core.models import TimeStampedModel

class Report(TimeStampedModel):
    """
    یک گزارش مالی
    """
    REPORT_TYPES = [
        ("balance_sheet", "ترازنامه"),
        ("profit_loss", "صورت سود و زیان"),
        ("cash_flow", "جریان وجوه نقد"),
        ("trial_balance", "تراز آزمایشی"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="financial_reports")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    generated_by = models.UUIDField(blank=True, null=True)  # user_id
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict, blank=True)  # داده‌های گزارش آماده استفاده در frontend یا export

    class Meta:
        verbose_name = "گزارش مالی"
        verbose_name_plural = "گزارش‌های مالی"
        ordering = ("-generated_at",)

    def __str__(self):
        return f"{self.get_report_type_display()} | {self.period_start} - {self.period_end}"

    def generate(self):
        """
        تولید گزارش بر اساس ledger summaries
        """
        summaries = LedgerSummary.objects.filter(
            organization=self.organization,
            period_start__lte=self.period_end,
            period_end__gte=self.period_start
        ).select_related('account')

        report_data = {}
        for s in summaries:
            acct_type = s.account.type
            if acct_type not in report_data:
                report_data[acct_type] = []
            report_data[acct_type].append({
                "account_code": s.account.code,
                "account_name": s.account.name,
                "opening_balance": float(s.opening_balance),
                "debit_total": float(s.debit_total),
                "credit_total": float(s.credit_total),
                "closing_balance": float(s.closing_balance),
            })

        self.data = report_data
        self.save()
        return self.data
