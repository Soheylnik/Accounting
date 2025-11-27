import uuid
from django.db import models
from core.models import Organization

# یک مدل abstract برای timestamp
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Account(TimeStampedModel):
    ACCOUNT_TYPES = [
        ("asset", "دارایی"),
        ("liability", "بدهی"),
        ("equity", "سرمایه"),
        ("income", "درآمد"),
        ("expense", "هزینه"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="accounts"
    )
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    parent_account = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children"
    )
    is_postable = models.BooleanField(default=True)

    class Meta:
        verbose_name = "حساب"
        verbose_name_plural = "حساب‌ها"
        unique_together = ("organization", "code")
        ordering = ("code",)

    def __str__(self):
        return f"{self.code} - {self.name}"

    def get_full_name(self):
        """نام کامل با نام parent (برای نمایش tree)"""
        if self.parent_account:
            return f"{self.parent_account.get_full_name()} > {self.name}"
        return self.name
