from django.contrib import admin
from .models import Genre, Book

class GenreAdmin(admin.ModelAdmin):
    model = Genre

class BookAdmin(admin.ModelAdmin):
    model = Book
    list_display = ('title', 'author', 'publication_year', 'genre')
    list_filter = ('genre', 'publication_year')
    search_fields = ('title', 'author')

admin.site.register(Genre, GenreAdmin)
admin.site.register(Book, BookAdmin)
