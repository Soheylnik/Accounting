from django.db import models
import uuid
from core.models import User, TimeStampedModel

class AuditLog(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="audit_logs")
    action = models.CharField(max_length=255)
    data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "لاگ عملیاتی"
        verbose_name_plural = "لاگ‌های عملیاتی"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.action} - {self.created_at:%Y-%m-%d %H:%M}"
