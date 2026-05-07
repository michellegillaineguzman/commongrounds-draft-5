from django import forms
from .models import Book, BookReview, Borrow

class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.update({'class': 'form-select form-select-cg'})
            else:
                field.widget.attrs.update({'class': 'form-control form-control-cg'})

class BookReviewForm(StyledModelForm):
    class Meta:
        model = BookReview
        fields = ['title', 'comment', 'anon_reviewer']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Review Title'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Share your thoughts...'}),
            'anon_reviewer': forms.TextInput(attrs={'placeholder': 'Optional: Anonymous Name'}),
        }

class BookContributionForm(StyledModelForm):
    new_genres = forms.CharField(
        required=False, 
        label="Add New Genres",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Mystery, Sci-Fi'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'genres' in self.fields:
            self.fields['genres'].required = False

    class Meta:
        model = Book
        fields = ['title', 'author', 'genres', 'new_genres', 'synopsis', 'publication_year', 'available_to_borrow']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. The Great Gatsby'}),
            'author': forms.TextInput(attrs={'placeholder': 'e.g. F. Scott Fitzgerald'}),
            'genres': forms.SelectMultiple(),
            'synopsis': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Briefly describe the story...'}),
            'publication_year': forms.NumberInput(attrs={'placeholder': 'YYYY'}),
        }

class BookUpdateForm(BookContributionForm):
    pass

class BorrowForm(StyledModelForm):
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
        return {'review': BookReviewForm, 'contribute': BookContributionForm, 'update': BookUpdateForm}.get(context)