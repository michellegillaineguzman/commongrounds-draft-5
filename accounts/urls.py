from django.urls import path

from .views import profile_update, register, dashboard

urlpatterns = [
    path('register', register, name='register'),
    path('dashboard', dashboard, name='dashboard'),
    path('<str:username>', profile_update, name='profile_update'),
]

app_name = 'accounts'