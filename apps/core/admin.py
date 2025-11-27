from django.contrib import admin
from .models import (
    Organization,
    OrganizationUser,
    OrganizationSettings,
    DocumentNumbering
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "tax_id", "base_currency", "timezone", "created_at")
    search_fields = ("name", "tax_id")
    list_filter = ("base_currency", "timezone")


@admin.register(OrganizationUser)
class OrganizationUserAdmin(admin.ModelAdmin):
    list_display = ("user", "organization", "role", "is_active", "created_at")
    list_filter = ("role", "is_active")
    search_fields = ("user__email", "user__username", "organization__name")


@admin.register(OrganizationSettings)
class OrganizationSettingsAdmin(admin.ModelAdmin):
    list_display = ("organization", "fiscal_year_start", "default_tax_rate", "decimal_places")
    search_fields = ("organization__name",)


@admin.register(DocumentNumbering)
class DocumentNumberingAdmin(admin.ModelAdmin):
    list_display = ("organization", "document_type", "prefix", "suffix", "next_number", "reset_period")
    list_filter = ("document_type", "reset_period")
    search_fields = ("organization__name",)
