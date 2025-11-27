from django.contrib import admin
from .models import Customer, Product, Invoice, InvoiceLine

class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 1
    autocomplete_fields = ("product",)
    fields = ("product", "description", "quantity", "unit_price", "line_total")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "contact", "email")
    list_filter = ("organization",)
    search_fields = ("name", "email")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "organization", "price", "track_inventory")
    list_filter = ("organization",)
    search_fields = ("name", "sku")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "customer", "organization", "status", "issue_date", "due_date", "total")
    list_filter = ("organization", "status", "issue_date")
    search_fields = ("invoice_number", "customer__name")
    ordering = ("-issue_date",)
    inlines = [InvoiceLineInline]
    autocomplete_fields = ("customer", "created_by")
