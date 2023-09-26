from django import forms

# TODO: create address/name form that listens to stripe's form
class OrderDetailsForm(forms.Form):
    name = forms.ChoiceField()
    address = forms.CharField() # should be stripe's address elem
