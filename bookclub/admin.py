from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Genre, Book, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]

class GenreAdmin(admin.ModelAdmin):
    model = Genre

class BookAdmin(admin.ModelAdmin):
    model = Book
    list_display = ('title', 'author', 'publication_year', 'genre')
    list_filter = ('genre', 'publication_year')
    search_fields = ('title', 'author')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Book, BookAdmin)
