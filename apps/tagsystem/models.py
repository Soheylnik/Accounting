import uuid
from django.db import models
from core.models import Organization, TimeStampedModel
from core.models import User

class Tag(TimeStampedModel):
    """
    برچسب عمومی برای سازمان
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="tags")
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#FFFFFF", help_text="رنگ هگز (#RRGGBB)")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"
        ordering = ("name",)
        unique_together = ("organization", "name")

    def __str__(self):
        return self.name


class TaggedItem(TimeStampedModel):
    """
    اتصال یک Tag به هر مدل دلخواه
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="items")
    content_type = models.CharField(max_length=100, help_text="مدل مربوطه مثل Invoice, Account, Product")
    object_id = models.UUIDField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "مورد برچسب خورده"
        verbose_name_plural = "موارد برچسب خورده"
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.tag.name} -> {self.content_type} ({self.object_id})"
