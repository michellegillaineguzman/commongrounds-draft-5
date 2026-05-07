from django import forms

from .models import Product, ProductType, Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount']


class ProductForm(forms.ModelForm):
    product_type = forms.ModelChoiceField(
        queryset=ProductType.objects.all(),
        widget=forms.Select(),
        required=False,
    )

    class Meta:
        model = Product
        fields = ['name', 'product_type', 'description', 'price', 'stock', 'status', 'product_image']
        widgets = {
            'status': forms.Select(),
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Tote Bag'}),
            'description': forms.Textarea(attrs={'placeholder': 'Describe your product...'}),
            'price': forms.NumberInput(attrs={'placeholder': 'e.g. 250.00'}),
            'stock': forms.NumberInput(attrs={'placeholder': 'e.g. 10'}),
        }