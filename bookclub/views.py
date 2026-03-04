from django.views.generic import ListView, DetailView
from .models import Book

class GenreListView(ListView):
    model = Book
    template_name = 'bookclub/genre_list.html'
    context_object_name = 'genres'


class BookDetailView(DetailView):
    model = Book
    template_name = 'bookclub/book_detail.html'
    context_object_name = 'book'
