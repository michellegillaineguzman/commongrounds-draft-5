from django.db import models
from django.urls import reverse
from accounts.models import Profile


class EventType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Event(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Full', 'Full'),
        ('Done', 'Done'),
        ('Cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        EventType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    organizer = models.ManyToManyField(
        Profile,
        blank=True,
        related_name='organized_events'
    )
    image = models.ImageField(upload_to='events/', null=True, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('localevents:event-detail', args=[self.pk])


class EventSignup(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user_registrant = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    new_registrant = models.CharField(max_length=255, blank=True)

    def __str__(self):
        if self.user_registrant:
            return f"{self.user_registrant} - {self.event}"
        return f"{self.new_registrant} - {self.event}"