from django import forms
from .models import Project, ProjectRating, ProjectReview

class ProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select form-select-cg'})
            else:
                field.widget.attrs.update({'class': 'form-control form-control-cg'})

    class Meta:
        model = Project
        fields = ['title', 'category', 'description', 'materials', 'steps']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'e.g. Handmade Ceramic Vase'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Briefly describe your project...'}),
            'materials': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List the materials needed, e.g. Clay, Pottery Wheel, Kiln...'}),
            'steps': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe the steps to complete your project...'}),
        }

class ProjectRatingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control form-control-cg'})

    class Meta:
        model = ProjectRating
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 10}),
        }

class ProjectReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control form-control-cg'})

    class Meta:
        model = ProjectReview
        fields = ['comment', 'image']
