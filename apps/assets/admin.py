from django.contrib import admin
from .models import FixedAsset

@admin.register(FixedAsset)
class FixedAssetAdmin(admin.ModelAdmin):
    list_display = ("asset_name", "organization", "purchase_date", "purchase_price", "depreciation_method")
    list_filter = ("organization", "depreciation_method")
    search_fields = ("asset_name",)
    ordering = ("purchase_date",)
