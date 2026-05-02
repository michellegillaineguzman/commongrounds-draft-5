from django.urls import path

from . import views

app_name = "commissions"

urlpatterns = [
    path("requests", views.CommissionListView.as_view(), name="request_list"),
    path("request/<int:pk>", views.CommissionDetailView.as_view(), name="request_detail"),
    path("request/add", views.CommissionCreateView.as_view(), name="request_create"),
    path("request/<int:pk>/edit", views.CommissionUpdateView.as_view(), name="request_update"),
    path("job/<int:pk>/apply", views.ApplyToJobView.as_view(), name="job_apply"),
]