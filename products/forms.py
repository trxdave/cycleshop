from django import forms
from .models import Product
from .models import Rating


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'price', 'stock', 'available',
            'sku', 'rating', 'image', 'category'
        ]

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating']  # Only allow the rating field

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
