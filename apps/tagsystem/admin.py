from django.contrib import admin
from .models import Tag, TaggedItem

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "color")
    list_filter = ("organization",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(TaggedItem)
class TaggedItemAdmin(admin.ModelAdmin):
    list_display = ("tag", "content_type", "object_id", "created_by")
    list_filter = ("content_type", "tag__organization")
    search_fields = ("tag__name",)
    autocomplete_fields = ("tag", "created_by")
