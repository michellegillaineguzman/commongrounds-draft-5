from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django import forms

from accounts.mixins import RoleRequiredMixin
from accounts.models import Profile

from .models import Event, EventSignup


class EventListView(ListView):
    model = Event
    template_name = 'localevents/event_list.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:

            profile = self.request.user.profile
            created = Event.objects.filter(organizer=profile)
            signed = Event.objects.filter(eventsignup__user_registrant=profile)

            all_events = Event.objects.exclude(id__in=created).exclude(id__in=signed)

            context['created_events'] = created
            context['signed_events'] = signed
            context['events'] = all_events

        return context



class EventDetailView(DetailView):
    model = Event
    template_name = 'localevents/event_detail.html'
    context_object_name = 'event'


class EventCreateView(RoleRequiredMixin, CreateView):
    model = Event
    template_name = 'localevents/event_form.html'
    required_role = "Event Organizer"

    fields = [
        'title',
        'category',
        'image',
        'description',
        'location',
        'start_time',
        'end_time',
        'capacity',
        'status'
    ]

    def form_valid(self, form):
        print("FORM VALID HIT")

        self.object = form.save()  

        self.object.organizer.add(self.request.user.profile)

        print("SAVED OBJECT:", self.object.pk)

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('localevents:event-detail', kwargs={'pk': self.object.pk})


class EventUpdateView(RoleRequiredMixin, UpdateView):
    model = Event

    fields = [
    'title',
    'category',
    'image',
    'description',
    'location',
    'start_time',
    'end_time',
    'capacity',
    'status'
    ]
    
    template_name = 'localevents/event_form.html'

    required_role = "Event Organizer"

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.object.eventsignup_set.count() >= self.object.capacity:
            self.object.status = "Full"
        else:
            self.object.status = "Available"

        self.object.save()
        return response

    def get_success_url(self):
        return reverse('localevents:event-detail', kwargs={'pk': self.object.pk})


class BaseSignupView(View):

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if not self.check_capacity(event):
            return redirect('localevents:event-detail', pk=event.pk)

        if not self.check_ownership(event, request.user):
            return redirect('localevents:event-detail', pk=pk)

        self.create_signup(event, request)

        return redirect(self.get_redirect_url(event))

    def check_capacity(self, event):
        return event.eventsignup_set.count() < event.capacity

    def check_ownership(self, event, user):
        if not user.is_authenticated:
            return True
        return user.profile not in event.organizer.all()

    def create_signup(self, event, request):
        raise NotImplementedError

    def get_redirect_url(self, event):
        return reverse('localevents:event-detail', kwargs={'pk': event.pk})


class EventSignupView(BaseSignupView):

    def create_signup(self, event, request):
        if request.user.is_authenticated:
            EventSignup.objects.create(
                event=event,
                user_registrant=request.user.profile
            )

class GuestSignupForm(forms.Form):
    name = forms.CharField(max_length=255)


class EventSignupFormView(FormView):
    template_name = 'localevents/event_signup.html'
    form_class = GuestSignupForm

    def form_valid(self, form):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])

        EventSignup.objects.create(
            event=event,
            new_registrant=form.cleaned_data['name']
        )

        return redirect('localevents:event-detail', pk=event.pk)