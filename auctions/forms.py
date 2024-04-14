from django import forms
from django.core.validators import MinValueValidator
from .models import all_bids
class new_listing_form(forms.Form): # this is a form that is created by django for data about a new listing on the commerce website
    title = forms.CharField(label="Title for the listing",max_length=80, required= True)
    description = forms.CharField(label="description", widget=forms.Textarea(attrs={'class':"description"}), required=True, max_length= 10000)
    image_url = forms.URLField(label="product image url (optional)", required=False)
    initial_bid = forms.FloatField(label="initial bid $",validators = [MinValueValidator(0)], required= True, widget=forms.NumberInput(attrs={'min': '0'}))
    category = forms.CharField(label="plz enter a Category",max_length=255, required= True)
class biding_form(forms.Form):
    current_bid = forms.FloatField(label="Your bid $",validators = [MinValueValidator(0)], required= True, widget=forms.NumberInput(attrs={'min': '0'}))
    listing_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
    # write coustom validators for this function today and also find  a way to add that vaildator to the html side aswell
    def clean(self):
        form_data = self.cleaned_data
        current_bid_of_this_listing = all_bids.objects.filter(for_which_listing = form_data['listing_id']).order_by('-bid').first()
        if form_data['current_bid'] < current_bid_of_this_listing.bid:
            self._errors["current_bid"] = self.error_class(["Bid must be larger than the last one"])
            del form_data['current_bid']
        return form_data
class comments_form(forms.Form):
    comment = forms.CharField(label="comment", widget=forms.Textarea(attrs={'class':"comment"}), required=False, max_length= 10000)
    listing_id = forms.IntegerField(widget=forms.HiddenInput(), required=True)
