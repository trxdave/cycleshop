from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    """Form for creating and editing orders."""

    class Meta:
        model = Order
        fields = (
            'full_name', 'email', 'phone_number',
            'address', 'city', 'postal_code', 'country',
        )

    def __init__(self, *args, **kwargs):
        """
        Add placeholders and classes, remove auto-generated
        labels, and set autofocus on the first field.
        """
        super().__init__(*args, **kwargs)

        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'address': 'Street Address',
            'city': 'City',
            'postal_code': 'Postal Code',
            'country': 'Country',
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True

        for field_name, placeholder_text in placeholders.items():
            field = self.fields.get(field_name)
            if field:
                required = field.required
                field.widget.attrs['placeholder'] = (
                    f"{placeholder_text}{' *' if required else ''}"
                )
                field.widget.attrs['class'] = 'form-control'
                field.label = False
