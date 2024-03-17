from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, listing, all_bids , comments
from .forms import new_listing_form

def index(request):
     # all this arg all requesting for the discription of the product which is not being user her but will in the listing page idiviudal
    all_the_listings = listing.objects.all().prefetch_related('bid')
    listing_data_with_bids=[]
    for each_listing in all_the_listings:
        data_of_each_listing = {
        'title': each_listing.title,
        'image_url': each_listing.image_url,
        'description': each_listing.description,
        'bid': each_listing.bid.filter(for_which_listing = each_listing.id).order_by('-bid').first()}
        listing_data_with_bids.append(data_of_each_listing)
    for i in range(len(listing_data_with_bids)):
        print(listing_data_with_bids[i]['bid'])
    return render(request, "auctions/index.html",{"listings_with_bids":listing_data_with_bids})
    # lastly I need to fix the inital bid funtion it will not work for updating the price there need to some logic for that as well 

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
        user_instance = User.objects.get(username= request.user.username) # plus I also wish to add user to sumbit there own images to me url way is clunky
        new_listing = listing(user = user_instance,title = request.POST["title"], description = request.POST["description"], image_url = request.POST["image_url"])
        new_listing.save()
        initial_bid = all_bids(user = user_instance , bid = request.POST["initial_bid"], for_which_listing = new_listing )
        initial_bid.save() # add a way to send a message that a new listing is seccsufly been created
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/new_listing.html",{"form": new_listing_form()})
        
    
    

