from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, OneTimePassword


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    ordering = ("-date_joined",)
    list_display = ("email", "full_name", "role", "phone_number", "is_active", "is_staff", "date_joined")
    search_fields = ("email", "full_name", "phone_number")
    list_filter = ("role", "is_active", "is_staff")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("full_name", "phone_number")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "role", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "phone_number", "password1", "password2", "is_staff", "is_active", "role"),
        }),
    )


@admin.register(OneTimePassword)
class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "user", "code", "purpose", "is_used", "expires_at", "created_at")
    list_filter = ("purpose", "is_used")
    search_fields = ("phone_number", "user__email")
    ordering = ("-created_at",)
