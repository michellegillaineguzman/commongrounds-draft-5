from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=63, blank=True)
    email = models.EmailField()

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile_detail', args=[str(self.id)])
    
    class Meta:
        ordering = ['display_name']

    def __str__(self):
        return self.user.username
    def get_absolute_url(self):
        return reverse('accounts:profile_detail', args=[self.user.username])