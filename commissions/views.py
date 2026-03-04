from django.views.generic import ListView, DetailView
from .models import Commission


class CommissionListView(ListView):
    model = Commission
    template_name = "commissions/request_list.html"
    context_object_name = "requests"


class CommissionDetailView(DetailView):
    model = Commission
    template_name = "commissions/request_detail.html"
    context_object_name = "request"