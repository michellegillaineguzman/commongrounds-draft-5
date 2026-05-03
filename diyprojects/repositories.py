from django.db.models import Avg
from .models import Project, ProjectCategory, ProjectReview, ProjectRating, Favorite

class ProjectRepository:

    def get_all(self):
        return Project.objects.all()
    
    def get_all_excluding(self, ids):
        return Project.objects.exclude(id__in=ids)
    
    def get_by_category(self, category_name):
        return Project.objects.filter(category__name=category_name)
    
    def get_recent(self, n):
        return Project.objects.order_by('-created_on')[:n]

    def get_by_id(self, id):
        return Project.objects.get(pk=id)

    def get_by_creator(self, profile):
        return Project.objects.filter(creator=profile)

    def get_favorited_by(self, profile):
        return Project.objects.filter(favorited_by__profile=profile)

    def get_reviewed_by(self, profile):
        return Project.objects.filter(reviews__reviewer=profile).distinct()

    def get_reviews_by_project(self, project):
        return project.reviews.all()

    def get_average_rating(self, project):
        return project.ratings.aggregate(Avg('score'))['score__avg']

    def get_favorite_count(self, project):
        return project.favorited_by.count()

    def is_favorited(self, project, profile):
        return Favorite.objects.filter(project=project, profile=profile).exists()

    def get_categories(self):
        return ProjectCategory.objects.all()

    def toggle_favorite(self, project, profile):
        favorite, created = Favorite.objects.get_or_create(project=project, profile=profile)
        if not created:
            favorite.delete()
            return False
        return True

    def add_or_update_rating(self, project, profile, score):
        rating, created = ProjectRating.objects.update_or_create(
            project=project, profile=profile,
            defaults={'score': score}
        )
        return rating

    def add_review(self, project, reviewer, comment, image=None):
        return ProjectReview.objects.create(
            project=project, reviewer=reviewer,
            comment=comment, image=image
        )

    def create_project(self, **data):
        return Project.objects.create(**data)

    def update_project(self, project, **data):
        for key, value in data.items():
            setattr(project, key, value)
        project.save()
        return project