from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import User, listing, all_bids , comments
from .forms import new_listing_form , biding_form, comments_form
from django.contrib import messages

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

def create_listing(request): # use the @login fuction provied by cs50 and add a way for user to login/register form the error page
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
def listing_page(request, listing_id):
    if request.method =="POST":
        try:
            form = biding_form(request.POST)
            if form.is_valid():
                user_instance = User.objects.get(username= request.user.username)
                this_listing = listing.objects.get(pk = listing_id)
                current_bid = all_bids(user = user_instance, bid = form.cleaned_data["current_bid"], for_which_listing = this_listing)
                current_bid.save() # find a way to prevent the owner of the bid to place a bid insted show them the option to end auction
                              # may be a different function for whishlist and catagories
                return HttpResponseRedirect(reverse("listing_page", args=[listing_id])) 
        
            else:
                which_listing = listing.objects.get(pk = listing_id)
                lastbid = which_listing.bid.filter(for_which_listing = listing_id).order_by('-bid').first()
                messages.error(request, f"There was an error. your bid must be greater then ${lastbid}")
                return HttpResponseRedirect(reverse("listing_page", args=[listing_id])) # find a way to tell user the bid was invaild message
        except ObjectDoesNotExist:
            return render(request, "auctions/error_page.html",{"error":"user must be signed in"})            
    else:

        
        try:
            which_listing = listing.objects.get(pk = listing_id)
            and_its_bid = which_listing.bid.filter(for_which_listing = listing_id).order_by('-bid').first()
            all_the_bids = all_bids.objects.all().filter(for_which_listing = listing_id).order_by('-bid')
            comments_for_this_listing = comments.objects.all().filter(for_which_listing = listing_id).order_by('-timestamp')
            if comments_for_this_listing.exists():
                all_comments = comments_for_this_listing
            else:
                all_comments = "wow such empty"    
            form = biding_form(initial ={'listing_id':listing_id})
            commenting_form = comments_form(initial ={'listing_id':listing_id})
            return render(request, "auctions/listing_page.html",{ "listing": which_listing, "bid": and_its_bid, "bid_histroy": all_the_bids, "form":form,"comments_form":commenting_form, "comment_section":all_comments})
    
        except ObjectDoesNotExist:
            return render(request, "auctions/error_page.html",{"error":"no listing found with this url try again"})
        
def comment_section(request):
    if request.method =="POST":
        try:
            form = comments_form(request.POST)
            if form.is_valid():
                user_instance = User.objects.get(username= request.user.username)
                this_listing = listing.objects.get(pk = form.cleaned_data["listing_id"])
                new_comment = comments(user = user_instance, comment = form.cleaned_data["comment"], for_which_listing = this_listing)
                new_comment.save()
                return HttpResponseRedirect(reverse("listing_page", args=[form.cleaned_data["listing_id"]]))
        except ObjectDoesNotExist:
            return render(request, "auctions/error_page.html",{"error":"user must be signed in"})