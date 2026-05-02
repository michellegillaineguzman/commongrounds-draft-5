from django.contrib import admin

from .models import CommissionType, Commission, Job, JobApplication


class JobInline(admin.TabularInline):
    model = Job
    extra = 1


@admin.register(CommissionType)
class CommissionTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "type",
        "maker",
        "people_required",
        "status",
        "created_on",
        "updated_on",
    ]
    list_filter = ["status", "type", "created_on"]
    search_fields = ["title", "description"]
    inlines = [JobInline]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = [
        "role",
        "commission",
        "manpower_required",
        "status",
    ]
    list_filter = ["status"]
    search_fields = ["role", "commission__title"]


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = [
        "job",
        "applicant",
        "status",
        "applied_on",
    ]
    list_filter = ["status", "applied_on"]
    search_fields = [
        "job__role",
        "job__commission__title",
        "applicant__display_name",
    ]