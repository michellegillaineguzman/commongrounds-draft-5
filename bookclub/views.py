from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, Bookmark, BookReview, Profile, Borrow
from .forms import BookFormFactory, BorrowForm
from datetime import timedelta

class BookListView(ListView):
    model = Book
    template_name = 'bookclub/book_list.html'
    context_object_name = 'all_books'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            profile = self.request.user.profile
            ctx['contributed'] = Book.objects.filter(contributor=profile)
            ctx['bookmarked'] = Bookmark.objects.filter(bookmarks__profile=profile)
            ctx['reviewed'] = BookReview.objects.filter(reviews__user_reviewer=profile)

            ctx['all_books']=ctx['all_books'].exclude(pk__in=ctx['contributed']).exclude(pk__in=ctx['bookmarked']).exclude(pk__in=ctx['reviewed'])
        return ctx

class BookDetailView(DetailView):
    model = Book
    template_name = 'bookclub/book_detail.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['review_form'] = BookFormFactory.get_form('review')()
        ctx['bookmark_count']= self.object.bookmarks.count()
        return ctx

    def post(self, request, *args, **kwargs):
        book = self.get_object()
        if 'bookmark' in request.POST and request.user.is_authenticated:
            Bookmark.objects.create(profile=request.user.profile, book=book)
        elif 'submit_review' in request.POST:
            form_class = BookFormFactory.get_form('review')
            form = form_class(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.book = book
                if request.user.is_authenticated:
                    review.user_reviewer = request.user.profile
                else:
                    review.anon_reviewer = "Anonymous"
                review.save()
        return redirect('bookclub:book_detail', pk=book.pk)

class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    template_name = 'bookclub/book_form.html'
    
    def get_form_class(self):
        return BookFormFactory.get_form('contribute')

    def form_valid(self, form):
        if self.request.user.profile.role == 'Contributor':
            return redirect('bookclub:book_list')
        form.instance.contributor = self.request.user.profile
        return super().form_valid(form)

class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    template_name = 'bookclub/book_form.html'

    def get_form_class(self):
        return BookFormFactory.get_form("update")
    
    def dispatch(self, request, *args, **kwargs):
        book = self.get_object()
        if book.contributor != request.user.profile or request.user.profile.role != 'Book Contributor':
            return redirect('bookclub:book_list')
        return super().dispatch(request, *args, **kwargs)

class BookBorrowView(LoginRequiredMixin, CreateView):
    model = Borrow
    template_name = 'bookclub/book_borrow.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        initial_data = {}
        if self.request.user.is_authenticated:
            initial_data['user'] = self.request.user
        ctx['form'] = BorrowForm(initial=initial_data)
        return ctx

    def post(self, request, *args, **kwargs):
        form = BorrowForm(request.POST)
        if form.is_valid():
            borrow = form.save(commit=False)
            borrow.book = self.get_object()
            if request.user.is_authenticated:
                borrow.borrower = request.user.profile

            borrow.date_to_return = borrow.date_borrowed + timedelta(days=14)
            borrow.save()
            return redirect('bookclub:book_detail', pk=borrow.book.pk)