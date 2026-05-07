from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .models import Project, Favorite, ProjectReview, ProjectRating
from .repositories import ProjectRepository
from .forms import ProjectForm, ProjectRatingForm, ProjectReviewForm
from accounts.mixins import RoleRequiredMixin

class ProjectListView(ListView):
    template_name = 'diyprojects/project_list.html'
    context_object_name = 'projects'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = ProjectRepository()

    def get_queryset(self):
        return self.repository.get_all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            profile = self.request.user.profile
            created_projects = self.repository.get_by_creator(profile)
            favorited_projects = self.repository.get_favorited_by(profile)
            reviewed_projects = self.repository.get_reviewed_by(profile)
            
            grouped_ids = set()
            for qs in [created_projects, favorited_projects, reviewed_projects]:
                for obj in qs:
                    grouped_ids.add(obj.id)
            
            context['created_projects'] = created_projects
            context['favorited_projects'] = favorited_projects
            context['reviewed_projects'] = reviewed_projects
            context['all_projects'] = self.repository.get_all_excluding(grouped_ids)
        else:
            context['all_projects'] = self.repository.get_all()
        return context

class ProjectDetailView(DetailView):
    template_name = 'diyprojects/project_detail.html'
    context_object_name = 'project'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = ProjectRepository()

    def get_object(self, queryset=None):
        project_id = self.kwargs.get('pk')
        return self.repository.get_by_id(project_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        context['average_rating'] = self.repository.get_average_rating(project)
        context['favorite_count'] = self.repository.get_favorite_count(project)
        context['reviews'] = self.repository.get_reviews_by_project(project)
        
        if self.request.user.is_authenticated:
            context['rating_form'] = ProjectRatingForm()
            context['review_form'] = ProjectReviewForm()
            context['is_favorited'] = self.repository.is_favorited(project, self.request.user.profile)
        
        return context

class ProjectCreateView(RoleRequiredMixin, CreateView):
    required_role = 'Project Creator'
    model = Project
    form_class = ProjectForm
    template_name = 'diyprojects/project_create.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = ProjectRepository()

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not hasattr(request.user, 'profile') or not request.user.profile.has_role('Project Organizer'):
            return redirect('permission_denied')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        project_data = form.cleaned_data
        project_data['creator'] = self.request.user.profile
        self.object = self.repository.create_project(**project_data)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('diyprojects:project_detail', kwargs={'pk': self.object.pk})

class ProjectUpdateView(RoleRequiredMixin, UpdateView):
    required_role = 'Project Creator'
    model = Project
    form_class = ProjectForm
    template_name = 'diyprojects/project_update.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = ProjectRepository()

    def form_valid(self, form):
        project = self.get_object()
        self.repository.update_project(project, **form.cleaned_data)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('diyprojects:project_detail', kwargs={'pk': self.object.pk})

class ProjectFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        repository = ProjectRepository()
        project = repository.get_by_id(pk)
        repository.toggle_favorite(project, request.user.profile)
        return redirect('diyprojects:project_detail', pk=pk)

class ProjectRatingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        repository = ProjectRepository()
        project = repository.get_by_id(pk)
        form = ProjectRatingForm(request.POST)
        if form.is_valid():
            repository.add_or_update_rating(
                project, request.user.profile, form.cleaned_data['score']
            )
        return redirect('diyprojects:project_detail', pk=pk)

class ProjectReviewView(LoginRequiredMixin, View):
    def post(self, request, pk):
        repository = ProjectRepository()
        project = repository.get_by_id(pk)
        form = ProjectReviewForm(request.POST, request.FILES)
        if form.is_valid():
            repository.add_review(
                project, request.user.profile, 
                form.cleaned_data['comment'], form.cleaned_data.get('image')
            )
        return redirect('diyprojects:project_detail', pk=pk)
