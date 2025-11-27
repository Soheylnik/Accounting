import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Organization(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    tax_id = models.CharField(max_length=50, blank=True)
    timezone = models.CharField(max_length=100, default="UTC")
    base_currency = models.CharField(
        max_length=3,
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{3}$",
                message="کد ارز باید شامل سه حرف بزرگ باشد (مانند USD یا IRR).",
            )
        ],
    )
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "سازمان"
        verbose_name_plural = "سازمان‌ها"
        ordering = ("name",)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("کاربران باید یک ایمیل داشته باشند.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("سوپر یوزر باید is_staff=True باشد.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("سوپر یوزر باید is_superuser=True باشد.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Roles(models.TextChoices):
        OWNER = "owner", "مالک"
        ADMIN = "admin", "مدیر"
        ACCOUNTANT = "accountant", "حسابدار"
        VIEWER = "viewer", "مشاهده‌گر"

    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_regex = RegexValidator(
        regex=r"^\+?\d{10,15}$",
        message="شماره موبایل باید بین ۱۰ تا ۱۵ رقم و فقط شامل عدد باشد (با امکان شروع با +).",
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=17,
        unique=True,
        validators=[phone_regex],
        help_text="شماره موبایل برای ورود با OTP استفاده می‌شود.",
    )
    phone_verified = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.ACCOUNTANT,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        ordering = ("full_name",)

    def __str__(self):
        return self.full_name or self.email


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


class OneTimePassword(models.Model):
    class Purposes(models.TextChoices):
        LOGIN = "login", "ورود"
        VERIFY_PHONE = "verify_phone", "تأیید شماره"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="otp_codes",
        null=True,
        blank=True,
    )
    phone_number = models.CharField(max_length=17, validators=[User.phone_regex])
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=Purposes.choices, default=Purposes.LOGIN)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "کد یکبار مصرف"
        verbose_name_plural = "کدهای یکبار مصرف"
        indexes = [
            models.Index(fields=("phone_number", "purpose")),
        ]

    def __str__(self):
        return f"{self.phone_number} - {self.code}"

    @property
    def is_expired(self):
        from django.utils import timezone

        return timezone.now() > self.expires_at
