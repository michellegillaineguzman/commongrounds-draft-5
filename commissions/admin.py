from django.contrib import admin
from .models import CommissionType, Commission


@admin.register(CommissionType)
class CommissionTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ("title", "people_required", "created_on", "updated_on")
    search_fields = ("title", "description")
    ordering = ("created_on",)
    list_filter = ("created_on",)