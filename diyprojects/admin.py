from django.contrib import admin
from .models import ProjectCategory, Project, Favorite, ProjectReview, ProjectRating


class ProjectCategoryAdmin(admin.ModelAdmin):
    model = ProjectCategory

class ProjectAdmin(admin.ModelAdmin):
    model = Project
    search_fields = ('title',)
    list_display = ('title', 'category', 'materials', 'created_on')
    list_filter = ('category',)

class FavoriteAdmin(admin.ModelAdmin):
    model = Favorite

class ProjectReviewAdmin(admin.ModelAdmin):
    model = ProjectReview
    list_display = ('reviewer', 'project', 'comment',)

class ProjectRatingAdmin(admin.ModelAdmin):
    model = ProjectRating
    list_filter = ('score',)


admin.site.register(ProjectCategory, ProjectCategoryAdmin)
admin.site.register(Project, ProjectAdmin)