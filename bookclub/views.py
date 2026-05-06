from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, Bookmark, BookReview, Profile, Borrow
from .forms import BookFormFactory, BorrowForm
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist

class BookListView(ListView):
    model = Book
    template_name = 'bookclub/book_list.html'
    context_object_name = 'all_books'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            # Use try/except as shown in "Filtering" Slide 4 and "Data" Slide 21
            try:
                profile = Profile.objects.get(user=user)
            except ObjectDoesNotExist:
                # Manual creation as shown in "Working with Data" Slide 21
                profile = Profile()
                profile.user = user
                profile.role = "Book Contributor"
                profile.save()

            # Filtering using related_names defined in models (Filtering Slide 13)
            ctx['contributed'] = Book.objects.filter(contributor=profile)
            ctx['bookmarked'] = Book.objects.filter(bookmarks__profile=profile)
            ctx['reviewed'] = Book.objects.filter(reviews__user_reviewer=profile).distinct()

            # Using exclude() as shown in "Filtering" Slide 4
            ctx['all_books'] = ctx['all_books']
        return ctx

class BookDetailView(DetailView):
    model = Book
    template_name = 'bookclub/book_detail.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Advanced Requirement: Using Factory
        ctx['review_form'] = BookFormFactory.get_form('review')()
        # Count bookmarks (Filtering Slide 13)
        ctx['bookmark_count'] = self.object.bookmarks.count()
        return ctx

    def post(self, request, *args, **kwargs):
        book = self.get_object()
        # Handling POST requests (POST Requests Slide 6/9)
        if 'bookmark' in request.POST and request.user.is_authenticated:
            # Logic to add bookmark
            b = Bookmark()
            b.profile = request.user.bookclub_profile
            b.book = book
            b.save()
        elif 'submit_review' in request.POST:
            form_class = BookFormFactory.get_form('review')
            form = form_class(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.book = book
                if request.user.is_authenticated:
                    review.user_reviewer = request.user.bookclub_profile
                else:
                    review.anon_reviewer = "Anonymous"
                review.save()
        return redirect('bookclub:book_detail', pk=book.pk)

class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    template_name = 'bookclub/book_form.html'
    # Hardcoded success URL (First View Slide 23)
    success_url = '/bookclub/books/'
    
    def get_form_class(self):
        return BookFormFactory.get_form('contribute')
    
    def dispatch(self, request, *args, **kwargs):
        # Ensure Profile exists with right role (Managing Users Slide 9)
        try:
            profile = request.user.bookclub_profile
        except ObjectDoesNotExist:
            profile = Profile()
            profile.user = request.user
            profile.role = "Book Contributor"
            profile.save()

        if profile.role != 'Book Contributor':
            return redirect('bookclub:book_list')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Set contributor (Working with Forms Slide 17)
        form.instance.contributor = self.request.user.bookclub_profile
        return super().form_valid(form)

class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    template_name = 'bookclub/book_form.html'
    success_url = '/bookclub/books/'

    def get_form_class(self):
        return BookFormFactory.get_form("update")
    
    def dispatch(self, request, *args, **kwargs):
        book = self.get_object()
        # Permission check (Managing Users Slide 9)
        if book.contributor != request.user.bookclub_profile:
            return redirect('bookclub:book_list')
        return super().dispatch(request, *args, **kwargs)

class BookBorrowView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'bookclub/book_borrow.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Pre-filling form (Working with Forms Slide 16)
        initial_data = {}
        if self.request.user.is_authenticated:
            initial_data['name'] = self.request.user.username
        ctx['form'] = BorrowForm(initial=initial_data)
        return ctx

    def post(self, request, *args, **kwargs):
        book = self.get_object()
        form = BorrowForm(request.POST)
        if form.is_valid():
            # Calculate and save (Working with Data Slide 14/21)
            borrow = form.save(commit=False)
            borrow.book = book
            borrow.borrower = request.user.bookclub_profile
            borrow.date_to_return = borrow.date_borrowed + timedelta(days=14)
            borrow.save()
            
            # Update book availability
            book.available_to_borrow = False
            book.save()
            
            return redirect('bookclub:book_detail', pk=book.pk)
        return self.get(request, *args, **kwargs)