from django import forms


class OrderDetailsForm(forms.Form):
    email = forms.EmailField()
    name = forms.CharField(max_length=100)
    country = forms.CharField(max_length=10)
    postal_code = forms.CharField(max_length=10)
    state = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    line1 = forms.CharField(max_length=100)
    line2 = forms.CharField(max_length=100, required=False)
    payment_intent = forms.CharField(max_length=100)
    save_address = forms.BooleanField(required=False)
