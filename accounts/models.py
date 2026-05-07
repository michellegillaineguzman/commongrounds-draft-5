from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=63, blank=True)
    email = models.EmailField()
    is_market_seller = models.BooleanField(default=False)
    is_event_organizer = models.BooleanField(default=False)
    is_book_contributor = models.BooleanField(default=False)
    is_project_creator = models.BooleanField(default=False)
    is_commission_maker = models.BooleanField(default=False)

    def has_role(self, role_name):
        mapping = {
            'Market Seller': self.is_market_seller,
            'Event Organizer': self.is_event_organizer,
            'Book Contributor': self.is_book_contributor,
            'Project Creator': self.is_project_creator,
            'Commission Maker': self.is_commission_maker,
        }
        return mapping.get(role_name, False)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('accounts:profile_detail', args=[self.user.username])
    
    class Meta:
        ordering = ['display_name']
