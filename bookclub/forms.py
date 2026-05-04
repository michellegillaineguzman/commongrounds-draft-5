from django import forms
from .models import Book, BookReview, Borrow

class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ['title', 'comment', 'anon_reviewer']

class BookContributionForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'synopsis', 'publication_year', 'available_to_borrow']

class BookUpdateForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['contributor']

class BookFormFactory:
    @classmethod
    def get_form(cls, context):
        if context == 'review':
            return BookReviewForm
        elif context == 'contribution':
            return BookContributionForm
        elif context == 'update':
            return BookUpdateForm
        else:
            raise ValueError("Invalid context for form factory")
        
class BorrowForm(forms.ModelForm):
    class Meta:
        model = Borrow
        fields = ['name','date_borrowed']
        widgets = {
            'date_borrowed': forms.TextInput(attrs={'type': 'date'}),
        }