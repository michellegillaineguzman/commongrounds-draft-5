from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.views import View
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from datetime import timedelta

from accounts.mixins import RoleRequiredMixin
from accounts.models import Profile

from .models import Book, Bookmark, BookReview, Borrow, Genre
from .forms import BookFormFactory, BorrowForm, BookReviewForm


class BookListView(ListView):
    model = Book
    template_name = 'bookclub/book_list.html'
    context_object_name = 'all_books'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
            profile = self.request.user.profile

            contributed = Book.objects.filter(contributor=profile).distinct()
            bookmarked = Book.objects.filter(bookmarks__profile=profile).distinct()
            borrowed = Book.objects.filter(borrow__borrower=profile).distinct()

            all_others = Book.objects.exclude(
                id__in=contributed
            ).exclude(
                id__in=bookmarked
            ).exclude(
                id__in=borrowed
            ).distinct()

            context['contributed'] = contributed
            context['bookmarked'] = bookmarked
            context['my_borrows'] = Borrow.objects.filter(borrower=profile)
            context['all_books'] = all_others

        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'bookclub/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object

        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
            profile = self.request.user.profile
            context['is_contributor'] = (book.contributor == profile)
            context['is_bookmarked'] = Bookmark.objects.filter(profile=profile, book=book).exists()
        else:
            context['is_contributor'] = False
            context['is_bookmarked'] = False

        if not book.available_to_borrow:
            context['current_borrow'] = Borrow.objects.filter(book=book).order_by('-date_borrowed').first()

        context['review_form'] = BookReviewForm()
        return context

    def post(self, request, *args, **kwargs):
        book = self.get_object()
        form = BookReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            if request.user.is_authenticated and hasattr(request.user, 'profile'):
                review.user_reviewer = request.user.profile
            review.save()
        return redirect('bookclub:book_detail', pk=book.pk)


class BookCreateView(RoleRequiredMixin, CreateView):
    model = Book
    template_name = 'bookclub/book_form.html'
    required_role = 'Book Contributor'

    def get_form_class(self):
        return BookFormFactory.get_form('contribute')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not hasattr(request.user, 'profile') or not request.user.profile.has_role('Book Contributor'):
            return redirect('permission_denied')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.contributor = self.request.user.profile
        self.object.save()
        form.save_m2m()
        
        new_genres_text = form.cleaned_data.get('new_genres')
        if new_genres_text:
            genre_names = [name.strip() for name in new_genres_text.split(',') if name.strip()]
            for name in genre_names:
                genre, _ = Genre.objects.get_or_create(name=name)
                self.object.genres.add(genre)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('bookclub:book_detail', kwargs={'pk': self.object.pk})


class BookUpdateView(RoleRequiredMixin, UpdateView):
    model = Book
    template_name = 'bookclub/book_form.html'
    required_role = 'Book Contributor'

    def get_form_class(self):
        return BookFormFactory.get_form('update')

    def dispatch(self, request, *args, **kwargs):
        book = get_object_or_404(Book, pk=kwargs['pk'])

        if not request.user.is_authenticated:
            return redirect('login')

        if (
            not hasattr(request.user, 'profile') or 
            not request.user.profile.has_role('Book Contributor') or 
            book.contributor != request.user.profile
        ):
            return redirect('permission_denied')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        new_genres_text = form.cleaned_data.get('new_genres')
        if new_genres_text:
            genre_names = [name.strip() for name in new_genres_text.split(',') if name.strip()]
            for name in genre_names:
                genre, _ = Genre.objects.get_or_create(name=name)
                self.object.genres.add(genre)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('bookclub:book_detail', kwargs={'pk': self.object.pk})


class BookmarkToggleView(View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            profile = request.user.profile
            bookmark_qs = Bookmark.objects.filter(profile=profile, book=book)
            if bookmark_qs.exists():
                bookmark_qs.delete()
            else:
                Bookmark.objects.create(profile=profile, book=book)
        return redirect('bookclub:book_detail', pk=book.pk)


class BookBorrowView(FormView):
    template_name = 'bookclub/book_borrow.html'
    form_class = BorrowForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = get_object_or_404(Book, pk=self.kwargs['pk'])
        return context

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial['name'] = self.request.user.username
        return initial

    def form_valid(self, form):
        book = get_object_or_404(Book, pk=self.kwargs['pk'])
        if not book.available_to_borrow:
            return redirect('bookclub:book_detail', pk=book.pk)

        borrow = form.save(commit=False)
        borrow.book = book
        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
            borrow.borrower = self.request.user.profile
        
        borrow.due_date = borrow.date_borrowed + timedelta(days=14)
        borrow.save()

        book.available_to_borrow = False
        book.save()

        return redirect('bookclub:book_detail', pk=book.pk)


def delete_review(request, pk):
    review = get_object_or_404(BookReview, pk=pk)
    book_pk = review.book.pk
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if review.user_reviewer == request.user.profile:
            review.delete()
    return redirect('bookclub:book_detail', pk=book_pk)