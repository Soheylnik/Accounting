from django.contrib import admin
from .models import TaxRate

@admin.register(TaxRate)
class TaxRateAdmin(admin.ModelAdmin):
    list_display = ("tax_name", "organization", "percentage")
    list_filter = ("organization",)
    search_fields = ("tax_name",)
    ordering = ("tax_name",)
