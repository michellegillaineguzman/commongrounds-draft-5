from django.db import models

class ProjectCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Project(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        ProjectCategory, on_delete=models.SET_NULL,
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