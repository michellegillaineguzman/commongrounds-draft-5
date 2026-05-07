from django import forms
from .models import Profile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name', 'is_market_seller', 'is_event_organizer', 
                  'is_book_contributor', 'is_project_creator', 'is_commission_maker']