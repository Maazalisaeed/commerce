from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, listing
from .forms import new_listing_form

def index(request):
    return render(request, "auctions/index.html",{"listings":listing.objects.all()})


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
        user_name = request.user.username
        user_instance = User.objects.get(username=user_name) # plus I also wish to add user to sumbit there own images to me url way is clunky
        new_listing = listing(user = user_instance,title = request.POST["title"], description = request.POST["description"], image_url = request.POST["image_url"], initial_bid = request.POST["initial_bid"])
        new_listing.save() # add a way to send a message that a new listing is seccsufly been created
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/new_listing.html",{"form": new_listing_form()})
        
    
    

