from django.contrib import admin
from .models import CostCenter

@admin.register(CostCenter)
class CostCenterAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "organization")
    list_filter = ("organization",)
    search_fields = ("code", "name")
    ordering = ("code",)
