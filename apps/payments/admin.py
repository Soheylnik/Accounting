from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "organization", "amount", "method", "paid_at", "created_by")
    list_filter = ("organization", "method", "paid_at")
    search_fields = ("invoice__invoice_number",)
    ordering = ("-paid_at",)
    autocomplete_fields = ("invoice", "from_bank_account", "to_bank_account", "created_by")
