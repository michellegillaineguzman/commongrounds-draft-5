from django.urls import path
from .views import (
    ProjectListView, ProjectDetailView, ProjectCreateView, 
    ProjectUpdateView, ProjectFavoriteView, ProjectRatingView,
    ProjectReviewView
)

app_name = 'diyprojects'

urlpatterns = [
    path('projects', ProjectListView.as_view(), name='project_list'),
    path('project/<int:pk>', ProjectDetailView.as_view(), name='project_detail'),
    path('project/add', ProjectCreateView.as_view(), name='project_create'),
    path('project/<int:pk>/edit', ProjectUpdateView.as_view(), name='project_update'),
    path('project/<int:pk>/favorite', ProjectFavoriteView.as_view(), name='project_favorite'),
    path('project/<int:pk>/rate', ProjectRatingView.as_view(), name='project_rate'),
    path('project/<int:pk>/review', ProjectReviewView.as_view(), name='project_review'),
]