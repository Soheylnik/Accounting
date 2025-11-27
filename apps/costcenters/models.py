import uuid
from django.db import models
from core.models import Organization, TimeStampedModel

class CostCenter(TimeStampedModel):
    """
    مرکز هزینه سازمان
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="cost_centers")
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "مرکز هزینه"
        verbose_name_plural = "مراکز هزینه"
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} - {self.name}"
