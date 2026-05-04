from django import forms

from .models import Commission, Job


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = [
            "title",
            "description",
            "type",
            "people_required",
            "status",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Band Logo Commission",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Describe your commission request...",
                "rows": 5,
            }),
            "people_required": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. 2",
                "min": 1,
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "type" in self.fields:
            self.fields["type"].widget.attrs.update({"class": "form-select"})
            self.fields["type"].empty_label = "Select commission type"


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "role",
            "manpower_required",
            "status",
        ]

        widgets = {
            "role": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Illustrator, Writer, Editor",
            }),
            "manpower_required": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. 1",
                "min": 1,
            }),
            "status": forms.Select(attrs={
                "class": "form-select",
            }),
        }