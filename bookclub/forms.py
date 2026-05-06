from django import forms
from .models import Book, BookReview, Borrow

class BookReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select form-select-cg'})
            else:
                field.widget.attrs.update({'class': 'form-control form-control-cg'})

    class Meta:
        model = BookReview
        fields = ['title', 'comment', 'anon_reviewer']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Review Title'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your thoughts on this book...'}),
            'anon_reviewer': forms.TextInput(attrs={'placeholder': 'Optional: Anonymous Name'}),
        }

class BookContributionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select form-select-cg'})
            else:
                field.widget.attrs.update({'class': 'form-control form-control-cg'})

    class Meta:
        model = Book
        fields = ['title', 'author', 'genre', 'synopsis', 'publication_year', 'available_to_borrow']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. The Great Gatsby'}),
            'author': forms.TextInput(attrs={'placeholder': 'e.g. F. Scott Fitzgerald'}),
            'synopsis': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Briefly describe the story...'}),
            'publication_year': forms.NumberInput(attrs={'placeholder': 'YYYY'}),
        }

class BookUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control form-control-cg'})

    class Meta:
        model = Book
        fields = ['available_to_borrow'] # Allow updates to availability

class BorrowForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control form-control-cg'})

    class Meta:
        model = Borrow
        fields = ['name', 'date_borrowed']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Your Full Name'}),
            'date_borrowed': forms.DateInput(attrs={'type': 'date'}),
        }

class BookFormFactory:
    @classmethod
    def get_form(cls, context):
        if context == 'review':
            return BookReviewForm
        elif context == 'contribute':
            return BookContributionForm
        elif context == 'update':
            return BookUpdateForm
        else:
            raise ValueError("Invalid context for form factory")