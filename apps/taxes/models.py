from django.db import models
import uuid
from core.models import Organization, TimeStampedModel

class TaxRate(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="tax_rates")
    tax_name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = "نرخ مالیات"
        verbose_name_plural = "نرخ‌های مالیاتی"
        ordering = ("tax_name",)
        unique_together = ("organization", "tax_name")

    def __str__(self):
        return f"{self.tax_name} ({self.percentage}%)"
