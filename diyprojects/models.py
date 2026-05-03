from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Profile

class ProjectCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Project Categories'

    def __str__(self):
        return self.name

class Project(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        ProjectCategory, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    creator = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, 
        null=True, blank=True
    )
    description = models.TextField()
    materials = models.TextField()
    steps = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title
    
class Favorite(models.Model):
    STATUS_CHOICES = [
        ('Backlog', 'Backlog'),
        ('To-Do', 'To-Do'),
        ('Done', 'Done'),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='favorited_by')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='favorites')
    date_favorited = models.DateField(auto_now_add=True)
    project_status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Backlog'
    )

    class Meta:
        ordering = ['-date_favorited']

    def __str__(self):
        return f"{self.profile.user.username} favorited {self.project.title}"

class ProjectReview(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='reviews')
    comment = models.TextField()
    image = models.ImageField(upload_to='project_reviews/', null=True, blank=True)

    def __str__(self):
        return f"Review by {self.reviewer.user.username} on {self.project.title}"

class ProjectRating(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings')
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    def __str__(self):
        return f"{self.score}/10 by {self.profile.user.username} on {self.project.title}"