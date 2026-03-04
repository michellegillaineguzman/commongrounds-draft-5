from django.contrib import admin
from .models import ProjectCategory, Project


class ProjectCategoryAdmin(admin.ModelAdmin):
    model = ProjectCategory

class ProjectAdmin(admin.ModelAdmin):
    model = Project
    search_fields = ('title',)
    list_display = ('title', 'category', 'materials', 'created_on')
    list_filter = ('category',)

admin.site.register(ProjectCategory, ProjectCategoryAdmin)
admin.site.register(Project, ProjectAdmin)