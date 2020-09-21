from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]


# form for cart
class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int  # convert the input into int
    )
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)

