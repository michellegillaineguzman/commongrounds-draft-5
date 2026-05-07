from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ProfileUpdateForm
from .models import Profile

def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        return redirect('login')
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_update(request, username):
    profile = get_object_or_404(Profile, user__username=username)
    form = ProfileUpdateForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('accounts:profile_update', username=username)
    
    return render(request, 'accounts/profile_update.html', {'form': form})

@login_required
def dashboard(request):
    profile = request.user.profile

    from merchstore.models import Product, Transaction
    from localevents.models import Event
    from diyprojects.models import Project
    from commissions.models import Commission

    products_sold = Transaction.objects.filter(
        product__owner=profile
    ).select_related('product', 'buyer')

    context = {
        'products': Product.objects.filter(owner=profile),
        'products_sold': products_sold,
        'events': Event.objects.filter(organizer__id=profile.id), 
        'projects': Project.objects.filter(creator=profile),
        'commissions': Commission.objects.filter(maker=profile),
    }

    from django.apps import apps
    if apps.is_installed('bookclub'):
        from bookclub.models import Book
        context['books'] = Book.objects.filter(contributor=profile)

    return render(request, 'accounts/dashboard.html', context)