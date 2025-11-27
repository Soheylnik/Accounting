from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import AuditLog, OneTimePassword, Organization, User


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "tax_id", "base_currency", "timezone", "created_at")
    search_fields = ("name", "tax_id")
    list_filter = ("base_currency", "timezone")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "full_name", "phone_number", "phone_verified", "organization", "role", "is_active")
    list_filter = ("role", "is_active", "phone_verified", "organization")
    search_fields = ("email", "full_name", "phone_number")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("اطلاعات شخصی", {"fields": ("full_name", "organization", "role", "phone_number", "phone_verified")}),
        ("دسترسی‌ها", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("تاریخ‌ها", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "phone_number", "organization", "role", "password1", "password2"),
            },
        ),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("action", "user__email", "data")


@admin.register(OneTimePassword)
class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "code", "purpose", "is_used", "expires_at")
    list_filter = ("purpose", "is_used", "expires_at")
    search_fields = ("phone_number", "code")
