from django import forms
from django.core.validators import MinValueValidator
class new_listing_form(forms.Form): # this is a form that is created by django for data about a new listing on the commerce website
    title = forms.CharField(label="Title for the listing",max_length=80, required= True)
    description = forms.CharField(label="description", widget=forms.Textarea(attrs={'class':"description"}), required=True, max_length= 10000)
    image_url = forms.URLField(label="product image url (optional)", required=False)
    initial_bid = forms.FloatField(label="initial bid $",validators = [MinValueValidator(0)], required= True, widget=forms.NumberInput(attrs={'min': '0'}))
class biding_form(forms.Form):
    current_bid = forms.FloatField(label="current bid $",validators = [MinValueValidator(0)], required= True, widget=forms.NumberInput(attrs={'min': '0'}))