from django.views.generic import ListView, DetailView
from .models import Project


class ProjectListView(ListView):
    model = Project
    template_name = 'diyprojects/project_list.html'
    context_object_name = 'projects'


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'diyprojects/project_detail.html'
    context_object_name = 'project'