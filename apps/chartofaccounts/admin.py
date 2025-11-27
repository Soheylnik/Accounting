from django.contrib import admin
from .models import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "type", "organization", "is_postable", "parent_account")
    list_filter = ("type", "is_postable", "organization")
    search_fields = ("code", "name")
    ordering = ("organization", "code")

    autocomplete_fields = ("parent_account",)
