from django.contrib import admin
from .models import Template, Meme

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "image_url", "created_at")
    search_fields = ("tags",)
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)

@admin.register(Meme)
class MemeAdmin(admin.ModelAdmin):
    list_display = ("id", "image_url", "user", "created_at")
    list_filter = ("created_at",)
