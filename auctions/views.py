from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, listing, all_bids , comments
from .forms import new_listing_form

def index(request):
    all_the_listings = listing.objects.all().order_by('-timestamp').prefetch_related('bid')
    listing_data_with_bids=[]
    for each_listing in all_the_listings:
        data_of_each_listing = {
        'title': each_listing.title,
        'listing_id': each_listing.pk,
        'image_url': each_listing.image_url,
        'description': each_listing.description,
        'timestamp': each_listing.timestamp,
        'bid': each_listing.bid.filter(for_which_listing = each_listing.id).order_by('-bid').first()}
        listing_data_with_bids.append(data_of_each_listing)   
    return render(request, "auctions/index.html",{"listings_with_bids":listing_data_with_bids})
     

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create_listing(request):
    if request.method =="POST":
        form = new_listing_form(request.POST)
        if form.is_valid():
            user_instance = User.objects.get(username= request.user.username) # plus I also wish to add user to sumbit there own images to me url way is clunky
            new_listing = listing(user = user_instance,title = form.cleaned_data["title"], description = form.cleaned_data["description"], image_url = form.cleaned_data["image_url"])
            new_listing.save()
            initial_bid = all_bids(user = user_instance , bid = form.cleaned_data["initial_bid"], for_which_listing = new_listing )
            initial_bid.save() # add a way to send a message that a new listing is seccsufly been created
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/new_listing.html",{"form": new_listing_form()})
    else:
        return render(request, "auctions/new_listing.html",{"form": new_listing_form()})
def listing_page(request, listing_id): #add comment section for this page 
    if request.method =="POST":
        pass
    else:
        
        try:
            which_listing = listing.objects.get(pk = listing_id)
            and_its_bid = which_listing.bid.filter(for_which_listing = listing_id).order_by('-bid').first()
            all_the_bids = all_bids.objects.all().filter(for_which_listing = listing_id).order_by('-bid')
            return render(request, "auctions/listing_page.html",{ "listing": which_listing, "bid": and_its_bid, "bid_histroy": all_the_bids, "form":new_listing_form})
    
        except ObjectDoesNotExist:
            return render(request, "auctions/error_page.html",{"error":"no listing found with this url try again"})
        
    
    

