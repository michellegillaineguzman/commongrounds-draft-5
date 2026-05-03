from django.urls import path
from .views import (
    EventListView,
    EventDetailView,
    EventCreateView,
    EventUpdateView,
    EventSignupView,
    EventSignupFormView,
)

app_name = 'localevents'

urlpatterns = [
    path('events', EventListView.as_view(), name='event-list'),
    path('event/add', EventCreateView.as_view(), name='event-create'),
    path('event/<int:pk>', EventDetailView.as_view(), name='event-detail'),
    path('event/<int:pk>/edit', EventUpdateView.as_view(), name='event-update'),
    path('event/<int:pk>/signup', EventSignupView.as_view(), name='event-signup'),
    path('event/<int:pk>/signup/form', EventSignupFormView.as_view(), name='event-signup-form'),
]
