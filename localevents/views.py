from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse

from accounts.mixins import RoleRequiredMixin

from .models import Event, EventSignup
from .forms import EventForm, GuestSignupForm


class EventListView(ListView):
    model = Event
    template_name = 'localevents/event_list.html'
    context_object_name = 'events'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            profile = self.request.user.profile

            created = Event.objects.filter(organizer=profile).distinct()
            signed = Event.objects.filter(
                eventsignup__user_registrant=profile
            ).distinct()

            all_events = Event.objects.exclude(
                id__in=created
            ).exclude(
                id__in=signed
            ).distinct()

            context['created_events'] = created
            context['signed_events'] = signed
            context['events'] = all_events

        return context


class EventDetailView(DetailView):
    model = Event
    template_name = 'localevents/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.object

        if self.request.user.is_authenticated:
            context['is_organizer'] = self.request.user.profile in event.organizer.all()
        else:
            context['is_organizer'] = False

        context['is_full'] = event.eventsignup_set.count() >= event.capacity
        return context


class EventCreateView(RoleRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'localevents/event_form.html'
    required_role = 'Event Organizer'

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.organizer.add(self.request.user.profile)
        return response

    def get_success_url(self):
        return reverse('localevents:event-detail', kwargs={'pk': self.object.pk})


class EventUpdateView(RoleRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'localevents/event_form.html'
    required_role = 'Event Organizer'

    def dispatch(self, request, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs['pk'])
        if request.user.is_authenticated:
            if request.user.profile not in event.organizer.all():
                return redirect('permission_denied')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)

        if self.object.eventsignup_set.count() >= self.object.capacity:
            self.object.status = 'Full'
        else:
            self.object.status = 'Available'

        self.object.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('localevents:event-detail', kwargs={'pk': self.object.pk})


class BaseSignupView(View):

    def get(self, request, pk):
        return redirect('localevents:event-detail', pk=pk)

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if not self.check_capacity(event):
            return redirect('localevents:event-detail', pk=event.pk)

        if not self.check_ownership(event, request.user):
            return redirect('localevents:event-detail', pk=pk)

        self.create_signup(event, request.user)

        return redirect(self.get_redirect_url(event))

    def check_capacity(self, event):
        return event.eventsignup_set.count() < event.capacity

    def check_ownership(self, event, user):
        if not user.is_authenticated:
            return True
        return user.profile not in event.organizer.all()

    def create_signup(self, event, user):
        raise NotImplementedError

    def get_redirect_url(self, event):
        return reverse('localevents:event-detail', kwargs={'pk': event.pk})


class EventSignupView(BaseSignupView):

    def create_signup(self, event, user):
        if user.is_authenticated:
            already_signed_up = EventSignup.objects.filter(
                event=event,
                user_registrant=user.profile
            ).exists()
            if not already_signed_up:
                EventSignup.objects.create(
                    event=event,
                    user_registrant=user.profile
                )


class EventSignupListRedirectView(EventSignupView):

    def get_redirect_url(self, event):
        return reverse('localevents:event-list')


class EventSignupFormView(FormView):
    template_name = 'localevents/event_signup.html'
    form_class = GuestSignupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = get_object_or_404(Event, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        event = get_object_or_404(Event, pk=self.kwargs['pk'])

        if event.eventsignup_set.count() >= event.capacity:
            return redirect('localevents:event-detail', pk=event.pk)

        EventSignup.objects.create(
            event=event,
            new_registrant=form.cleaned_data['name']
        )
        return redirect('localevents:event-detail', pk=event.pk)