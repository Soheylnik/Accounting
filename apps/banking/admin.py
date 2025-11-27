from django.contrib import admin
from .models import BankAccount, Reconciliation

@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("bank_name", "account_number", "organization", "balance")
    list_filter = ("organization", "bank_name")
    search_fields = ("bank_name", "account_number")
    ordering = ("organization", "bank_name", "account_number")


@admin.register(Reconciliation)
class ReconciliationAdmin(admin.ModelAdmin):
    list_display = ("bank_account", "start_date", "end_date", "statement_balance", "created_by")
    list_filter = ("bank_account__organization", "start_date", "end_date")
    search_fields = ("bank_account__bank_name", "bank_account__account_number")
    ordering = ("-end_date",)
    autocomplete_fields = ("bank_account", "created_by")
