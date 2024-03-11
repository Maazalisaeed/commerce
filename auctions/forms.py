from django import forms
from django.core.validators import MinValueValidator
class new_listing_form(forms.Form): # try usin the initial function to add some value to this form I hope it works
    user = forms.CharField(max_length=150, widget=forms.HiddenInput())
    title = forms.CharField(max_length=80)
    discription = forms.Textarea(max_length = 10000)
    image_url = forms.URLField()
    initial_bid = forms.FloatField(validators = [MinValueValidator(0)])
