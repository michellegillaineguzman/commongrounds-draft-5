from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['organizer']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g. Community Art Fair'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe your event...'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'e.g. Legazpi Sunday Market, Makati'
            }),
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local'
            }),
            'capacity': forms.NumberInput(attrs={
                'placeholder': 'e.g. 50'
            }),
            'category': forms.Select(),
            'status': forms.Select(),
        }
        labels = {
            'title': 'Event Title',
            'image': 'Event Image',
            'start_time': 'Start Date & Time',
            'end_time': 'End Date & Time',
            'capacity': 'Event Capacity',
        }


class GuestSignupForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        label='Your Name',
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Juan dela Cruz'
        })
    )