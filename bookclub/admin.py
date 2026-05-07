from django.contrib import admin
from .models import Genre, Book

class GenreAdmin(admin.ModelAdmin):
    model = Genre

class BookAdmin(admin.ModelAdmin):
    model = Book
    list_display = ('title', 'author', 'publication_year', 'get_genres')
    list_filter = ('genres', 'publication_year')
    
    search_fields = ('title', 'author')
    
    filter_horizontal = ('genres',)

    def get_genres(self, obj):
        return ", ".join([g.name for g in obj.genres.all()])
    
    get_genres.short_description = 'Genres'
admin.site.register(Genre, GenreAdmin)
admin.site.register(Book, BookAdmin)