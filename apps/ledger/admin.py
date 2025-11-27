from django.contrib import admin
from .models import LedgerEntry, LedgerSummary

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "account", "organization", "debit", "credit", "balance")
    list_filter = ("organization", "account", "date")
    search_fields = ("account__name",)
    ordering = ("organization", "account", "date")


@admin.register(LedgerSummary)
class LedgerSummaryAdmin(admin.ModelAdmin):
    list_display = ("account", "organization", "period_start", "period_end", "opening_balance", "debit_total", "credit_total", "closing_balance")
    list_filter = ("organization", "account")
    search_fields = ("account__name",)
    ordering = ("organization", "account", "period_start")
