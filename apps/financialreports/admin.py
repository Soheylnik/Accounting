from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("report_type", "organization", "period_start", "period_end", "generated_at")
    list_filter = ("organization", "report_type", "period_start", "period_end")
    search_fields = ("organization__name",)
    ordering = ("-generated_at",)
