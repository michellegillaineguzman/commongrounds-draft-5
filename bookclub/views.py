from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, Bookmark, Profile, Borrow
from accounts.models import Profile
from .forms import BookFormFactory, BorrowForm
from datetime import timedelta
from django.urls import reverse_lazy

class BookListView(ListView):
    model = Book
    template_name = 'bookclub/book_list.html'
    context_object_name = 'all_books'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            profile, created = Profile.objects.get_or_create(user=user)
            if created:
                profile.role = "Book Contributor"
                profile.save()

            contributed = Book.objects.filter(contributor=profile)
            bookmarked = Book.objects.filter(bookmarks__profile=profile)
            reviewed = Book.objects.filter(reviews__user_reviewer=profile).distinct()

            ctx['contributed'] = contributed
            ctx['bookmarked'] = bookmarked
            ctx['reviewed'] = reviewed

            ctx['my_borrows'] = Borrow.objects.filter(borrower=profile)

            ctx['all_books'] = ctx['all_books']
        return ctx

class BookDetailView(DetailView):
    model = Book
    template_name = 'bookclub/book_detail.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['review_form'] = BookFormFactory.get_form('review')()
        ctx['bookmark_count'] = self.object.bookmarks.count()

        if not self.object.available_to_borrow:
            ctx['current_borrow'] = Borrow.objects.filter(book=self.object).order_by('-date_borrowed').first()
        
        ctx['is_bookmarked'] = False
        if self.request.user.is_authenticated:
            profile, _ = Profile.objects.get_or_create(user=self.request.user)
            ctx['is_bookmarked'] = Bookmark.objects.filter(profile=profile, book=self.object).exists()
        return ctx

    def post(self, request, *args, **kwargs):
        book = self.get_object()
        if not request.user.is_authenticated:
            return redirect('login')

        profile, _ = Profile.objects.get_or_create(user=request.user)

        if 'bookmark' in request.POST:
            existing = Bookmark.objects.filter(profile=profile, book=book)
            if existing.exists():
                existing.delete()
            else:
                Bookmark.objects.create(profile=profile, book=book)

        elif 'submit_review' in request.POST:
            form_class = BookFormFactory.get_form('review')
            form = form_class(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.book = book
                review.user_reviewer = profile
                review.save()
        
        return redirect('bookclub:book_detail', pk=book.pk)

class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    template_name = 'bookclub/book_form.html'
    success_url = reverse_lazy('bookclub:book_list')
    
    def get_form_class(self):
        return BookFormFactory.get_form('contribute')
    
    def dispatch(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if profile.role != 'Book Contributor':
            profile.role = 'Book Contributor'
            profile.save()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        profile, _ = Profile.objects.get_or_create(user=self.request.user)
        form.instance.contributor = profile
        return super().form_valid(form)

class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    template_name = 'bookclub/book_form.html'
    success_url = reverse_lazy('bookclub:book_list')

    def get_form_class(self):
        return BookFormFactory.get_form("update")
    
    def dispatch(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        book = self.get_object()
        if book.contributor != profile:
            return redirect('bookclub:book_list')
        return super().dispatch(request, *args, **kwargs)

class BookBorrowView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'bookclub/book_borrow.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        initial_data = {'name': self.request.user.username}
        ctx['form'] = BorrowForm(initial=initial_data)
        return ctx

    def post(self, request, *args, **kwargs):
        book = self.get_object()
        
        if not book.available_to_borrow:
            return redirect('bookclub:book_detail', pk=book.pk)

        form = BorrowForm(request.POST)
        if form.is_valid():
            borrow = form.save(commit=False)
            borrow.book = book
            
            profile, _ = Profile.objects.get_or_create(user=request.user)
            borrow.borrower = profile
            
            borrow.due_date = borrow.date_borrowed + timedelta(days=14)
            borrow.save()
            
            book.available_to_borrow = False
            book.save()
            
            return redirect('bookclub:book_detail', pk=book.pk)
        return self.get(request, *args, **kwargs)