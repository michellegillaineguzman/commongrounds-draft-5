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
    new_genres = forms.CharField(
        required=False, 
        label="Add New Genres",
        help_text="Separate multiple genres with commas (e.g. Mystery, Thriller)",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Mystery, Sci-Fi'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['genres'].required = False
        
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.update({'class': 'form-select form-select-cg'})
            else:
                field.widget.attrs.update({'class': 'form-control form-control-cg'})

    class Meta:
        model = Book
        fields = ['title', 'author', 'genres', 'new_genres', 'synopsis', 'publication_year', 'available_to_borrow']
        widgets = {
            'genres': forms.SelectMultiple(),
            'synopsis': forms.Textarea(attrs={'rows': 5}),
        }

    def clean(self):
        cleaned_data = super().clean()
        genres = cleaned_data.get('genres')
        new_genres = cleaned_data.get('new_genres')

        if not genres and not new_genres:
            raise forms.ValidationError("You must either select an existing genre or input a new one.")
        
        return cleaned_data

class BookUpdateForm(forms.ModelForm):
    new_genres = forms.CharField(
        required=False, 
        label="Add New Genres",
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Mystery, Sci-Fi'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['genres'].required = False 
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.update({'class': 'form-select form-select-cg'})
            else:
                field.widget.attrs.update({'class': 'form-control form-control-cg'})

    class Meta:
        model = Book
        fields = ['title', 'author', 'genres', 'new_genres', 'synopsis', 'publication_year', 'available_to_borrow']

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('genres') and not cleaned_data.get('new_genres'):
            raise forms.ValidationError("Please provide at least one genre.")
        return cleaned_data

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