import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

# از core فقط ارجاع می‌زنیم (نباید core به accounts ارجاع بده، پس circular نیست)
from core.models import Organization  # فقط برای type-hint و برخی چک‌ها (اختیاری)


PHONE_REGEX = RegexValidator(
    regex=r"^\+?\d{10,15}$",
    message="شماره موبایل باید بین ۱۰ تا ۱۵ رقم باشد (امکان شروع با +).",
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("آدرس ایمیل الزامی است.")
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
    """
    Custom user model:
      - username removed, email used as USERNAME_FIELD
      - no direct FK to Organization (multi-org via core.OrganizationUser)
    """
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    full_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(
        max_length=17,
        unique=True,
        validators=[PHONE_REGEX],
        help_text="شماره موبایل برای ورود با OTP یا ارتباط استفاده می‌شود.",
    )
    phone_verified = models.BooleanField(default=False)

    class Roles(models.TextChoices):
        OWNER = "owner", "مالک"
        ADMIN = "admin", "مدیر"
        ACCOUNTANT = "accountant", "حسابدار"
        VIEWER = "viewer", "مشاهده‌گر"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.ACCOUNTANT)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # برای دسترسی به admin

    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        ordering = ("full_name",)

    def __str__(self):
        return self.full_name or self.email

    # helper: لیست سازمان‌هایی که کاربر عضو آن‌هاست
    def get_organizations(self):
        """
        برمی‌گرداند queryset از Organization که کاربر عضوشان است.
        نیاز به core.OrganizationUser دارد.
        """
        from core.models import OrganizationUser  # import local برای جلوگیری از circular import در ماژول لود
        return Organization.objects.filter(members__user=self, members__is_active=True)

    def is_member_of(self, organization):
        from core.models import OrganizationUser
        return OrganizationUser.objects.filter(organization=organization, user=self, is_active=True).exists()

    def primary_organization(self):
        """
        انتخاب یک سازمان پیش‌فرض برای کاربر (مثلاً اولین عضو active).
        در صورت نیاز می‌تونیم priority اضافه کنیم.
        """
        org = self.get_organizations().first()
        return org


class OneTimePassword(models.Model):
    class Purposes(models.TextChoices):
        LOGIN = "login", "ورود"
        VERIFY_PHONE = "verify_phone", "تأیید شماره"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otp_codes",
        null=True,
        blank=True,
    )
    phone_number = models.CharField(max_length=17, validators=[PHONE_REGEX])
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
        return timezone.now() > self.expires_at
