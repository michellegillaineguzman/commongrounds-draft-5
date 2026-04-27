from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def permission_denied(request):
    return render(request, '403.html')