from django.db import models
import uuid
from core.models import Organization, TimeStampedModel

class FixedAsset(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="assets")
    asset_name = models.CharField(max_length=255)
    purchase_date = models.DateField()
    purchase_price = models.DecimalField(max_digits=18, decimal_places=2)
    salvage_value = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    depreciation_method = models.CharField(max_length=50, default="straight_line")

    class Meta:
        verbose_name = "دارایی ثابت"
        verbose_name_plural = "دارایی‌های ثابت"
        ordering = ("purchase_date",)

    def __str__(self):
        return self.asset_name
