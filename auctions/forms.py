from django import forms
from django.core.validators import MinValueValidator
from .models import all_bids
categories =( 
    ("Fashion", "Fashion"), 
    ("Electronics", "Electronics"), 
    ("Home & Garden", "Home & Garden"), 
    ("Collectibles & Hobbies", "Collectibles & Hobbies"), 
    ("Sports & Outdoors", "Sports & Outdoors"),
    ("Vehicles","Vehicles"),
    ("Others","Others"), 
)
class new_listing_form(forms.Form): # this is a form that is created by django for data about a new listing on the commerce website
    title = forms.CharField(label="Listing Title",max_length=80, required= True,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Title','aria-label':'Title','aria-describedby':'basic-addon1'}))
    description = forms.CharField(label="description", widget=forms.Textarea(attrs={'class':'form-control','aria-label':'Description'}), required=True, max_length= 10000)
    image_url = forms.URLField(label="product image url (optional)", required=False, widget=forms.URLInput(attrs={'class': 'form-control','id':'basic-url','aria-describedby':'basic-addon3 basic-addon4'}))
    initial_bid = forms.FloatField(label="Initial bid $",validators = [MinValueValidator(0)], required= True, widget=forms.NumberInput(attrs={'min': '0','class':'form-control','aria-label':'Amount in USD only'}))
    category = forms.ChoiceField(choices = categories,required=True,widget=forms.Select(attrs={'class': 'form-select','id':'inputGroupSelect01'}))
class biding_form(forms.Form):
    current_bid = forms.FloatField(label="Your bid $",validators = [MinValueValidator(0)], required= True, widget=forms.NumberInput(attrs={'min': '0','class':'form-control'}))
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
    comment = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control','id':'floatingTextarea','spellcheck':'false','placeholder':'Leave a comment here'}), required=False, max_length= 10000, label="")
class listing_id_form(forms.Form):
    hidden_listing_id = forms.IntegerField(widget=forms.HiddenInput(), required=True) 
