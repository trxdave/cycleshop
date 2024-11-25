from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'stock', 'available',
            'sku', 'rating', 'image', 'category'
        ]


class RatingForm(forms.Form):
    RATING_CHOICES = [
        (1, '1 - Very Poor'),
        (2, '2 - Poor'),
        (3, '3 - Average'),
        (4, '4 - Good'),
        (5, '5 - Excellent'),
    ]
    rating = forms.ChoiceField(
        choices=RATING_CHOICES, widget=forms.RadioSelect
    )


class AddToWishlistForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = []
