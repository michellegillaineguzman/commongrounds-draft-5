from django.urls import path
from . import views

app_name = "commissions"

urlpatterns = [
    path("requests", views.CommissionListView.as_view(), name="request_list"),
    path("request/<int:pk>", views.CommissionDetailView.as_view(), name="request_detail"),
]