from django.contrib import admin
from .models import JournalEntry, JournalLine


class JournalLineInline(admin.TabularInline):
    model = JournalLine
    extra = 1
    autocomplete_fields = ("account", "cost_center")
    fields = ("account", "dc_indicator", "amount", "cost_center", "project_id")


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("entry_date", "reference", "organization", "status", "created_by", "created_at")
    list_filter = ("organization", "status", "entry_date")
    search_fields = ("reference", "description")
    ordering = ("-entry_date",)
    inlines = [JournalLineInline]
    autocomplete_fields = ("created_by",)

@admin.register(JournalLine)
class JournalLineAdmin(admin.ModelAdmin):
    list_display = ("journal_entry", "account", "dc_indicator", "amount", "cost_center")
    list_filter = ("dc_indicator", "account", "cost_center")
    search_fields = ("account__name", "journal_entry__reference")
