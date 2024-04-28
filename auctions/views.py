import re
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import User, listing, all_bids , comments, wishlist
from .forms import new_listing_form , biding_form, comments_form,listing_id_form
from django.contrib import messages
from . import util # added this samll comment 

def index(request):
    all_the_listings = listing.objects.order_by('-timestamp').prefetch_related('bid')
    listing_data_with_bids = util.display_listing(all_the_listings,False)
    return render(request, "auctions/index.html",{"listings":listing_data_with_bids})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user) # put a message here
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, 'you are successfully Logged out ')
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
            user = User.objects.create_user(username, email, password) # type: ignore
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
            new_listing = listing(user = user_instance,title = form.cleaned_data["title"], description = form.cleaned_data["description"], image_url = form.cleaned_data["image_url"], category = form.cleaned_data["category"], is_auction_active = "True")
            new_listing.save()
            initial_bid = all_bids(user = user_instance , bid = form.cleaned_data["initial_bid"], for_which_listing = new_listing)
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
                current_bid.save()
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
            and_its_bid = which_listing.bid.order_by('-bid').first()
            all_the_bids = all_bids.objects.all().filter(for_which_listing = listing_id).order_by('-bid')
            comments_for_this_listing = comments.objects.all().filter(for_which_listing = listing_id).order_by('-timestamp')
            if comments_for_this_listing.exists():
                all_comments = comments_for_this_listing
                total_comments = comments.objects.all().filter(for_which_listing = listing_id).count()
            else:
                all_comments = "wow such empty"
                total_comments = 0    
            bid_form = biding_form(initial ={'listing_id':listing_id})
            hidden_listing_id_form = listing_id_form(initial ={'hidden_listing_id':listing_id})
            return render(request, "auctions/listing_page.html",{ "listing": which_listing, "bid": and_its_bid, "bid_histroy": all_the_bids, "bid_form":bid_form,"comments_form":comments_form, "hidden_listing_id":hidden_listing_id_form, "comment_section":all_comments,"total_comments":total_comments})
    
        except ObjectDoesNotExist:
            return render(request, "auctions/error_page.html",{"error":"no listing found with this url try again"})
@login_required(login_url='/login') # add a way that there is message pop up the user must be login/registered        
def comment_section(request):
    if request.method =="POST":
        form = comments_form(request.POST)
        id_form = listing_id_form(request.POST)
        if form.is_valid() and id_form.is_valid():
            user_instance = User.objects.get(username= request.user.username)
            this_listing = listing.objects.get(pk = id_form.cleaned_data["hidden_listing_id"])
            new_comment = comments(user = user_instance, comment = form.cleaned_data["comment"], for_which_listing = this_listing)
            new_comment.save()
            return HttpResponseRedirect(reverse("listing_page", args=[id_form.cleaned_data["hidden_listing_id"]]))
    else:
        return HttpResponse("will make this page aswell")
@login_required(login_url='/login')
def wishlistfunction(request):
    user_instance = User.objects.get(username= request.user.username)
    if request.method =="POST":
        try:
            id_form = listing_id_form(request.POST)
            if id_form.is_valid():
                if wishlist.objects.filter(user = user_instance).exists():
                    add_to_wishlist = wishlist.objects.get(user = user_instance)
                    add_to_wishlist.for_which_listing.add(id_form.cleaned_data["hidden_listing_id"])
                    messages.success(request, 'this item added to your wishlist')
                    return HttpResponseRedirect(reverse("listing_page", args=[id_form.cleaned_data["hidden_listing_id"]]))
                else:    
                    new_wish_list_item = wishlist()
                    new_wish_list_item.save()
                    new_wish_list_item.user.set([user_instance])
                    new_wish_list_item.for_which_listing.set([id_form.cleaned_data["hidden_listing_id"]])
                    messages.success(request, 'this item added to your wishlist')
                return HttpResponseRedirect(reverse("listing_page", args=[id_form.cleaned_data["hidden_listing_id"]]))
        except ObjectDoesNotExist:
            return render(request, "auctions/error_page.html",{"error":"no listing found with this url try again"})
    else:
        all_wishlist_items = wishlist.objects.all().filter(user = user_instance).order_by('-timestamp')
        wishlish_data_with_bids = []
        for each_item in all_wishlist_items:
            wishlish_data_with_bids.extend(util.display_listing(each_item,True))    
        return render(request, "auctions/wishlist.html",{"wishlist":wishlish_data_with_bids})
def delwislist(request):
    if request.method =="POST":
        user_instance = User.objects.get(username= request.user.username)
        listing_id = listing.objects.get(pk = request.POST['wishlist_id'])
        delete_wishlist_item = wishlist.objects.get(user = user_instance, for_which_listing = request.POST['wishlist_id'])
        if delete_wishlist_item.for_which_listing.count() == 1:
            delete_wishlist_item.delete()
            return HttpResponseRedirect(reverse('wishlist'))
        else:
            delete_wishlist_item.for_which_listing.remove(listing_id)
            return HttpResponseRedirect(reverse('wishlist'))
    else:
        return render(request, "auctions/error_page.html",{"error":"no entery fuck off "})

def categories(request):
    if request.method =="POST":
        which_catagory = request.POST["category_name"]
        category_item = listing.objects.all().filter(category = which_catagory).prefetch_related('bid').order_by('-timestamp')
        listing_data_with_bids = util.display_listing(category_item,False)
        return render(request, "auctions/index.html",{"listings_with_bids":listing_data_with_bids})
        
    else:
        all_categories = listing. objects.values('category').annotate(total=Count('category')) 
        return render(request, "auctions/categories.html",{"all_categories":all_categories})
def close_auction(request):
    if request.method =="POST":
        id_form = request.POST["hidden_id"]
        closeing_auction = listing.objects.get(pk = id_form)
        winning_bidder = closeing_auction.bid.order_by('-bid').first()
        closeing_auction.is_auction_active = False
        closeing_auction.save()    
        messages.success(request, f'this listing has been cloed and the winning bidder is {winning_bidder.user}')
        return HttpResponseRedirect(reverse("HQ"))
            

def delete_auction(request):
    if request.method =="POST":
        id_form = request.POST["hidden_id"]
        deleteing_auction = listing.objects.get(pk = id_form)
        deleteing_auction.delete()
        messages.success(request, 'this listing has been been Deleted')
        return HttpResponseRedirect(reverse("HQ"))

@login_required(login_url='/login')
def controll(request):
    user_instance = User.objects.get(username= request.user.username)
    user_listings = listing.objects.filter(user = user_instance).order_by('-timestamp').prefetch_related('bid')
    listing_data_with_bids = util.display_listing(user_listings,False)
    
    return render(request, "auctions/controll_center.html",{"listings":listing_data_with_bids})
def delete_comment(request):
    id_form = request.POST["comment_id"]
    deleteing_comment = comments.objects.get(pk = id_form)
    listing_id =  deleteing_comment.for_which_listing.id
    deleteing_comment.delete()
    messages.success(request, 'Your Comment deleted successfuly')
    return HttpResponseRedirect(reverse("listing_page", args=[listing_id]))

