from django.contrib import admin
from .models import EventType, Event


class EventTypeAdmin(admin.ModelAdmin):
    model = EventType


class EventAdmin(admin.ModelAdmin):
    model = Event
    list_display = ('title', 'category', 'location', 'start_time', 'created_on')
    list_filter = ('category',)
    search_fields = ('title',)


admin.site.register(EventType, EventTypeAdmin)
admin.site.register(Event, EventAdmin)