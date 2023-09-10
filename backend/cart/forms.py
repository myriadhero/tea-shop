from django import forms


class CartItemForm(forms.Form):
    product_slug = forms.CharField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(required=False, initial=1, min_value=1)
    set_quantity = forms.BooleanField(
        required=False, initial=False, widget=forms.HiddenInput()
    )
    remove_from_cart = forms.BooleanField(
        required=False, initial=False, widget=forms.HiddenInput()
    )
