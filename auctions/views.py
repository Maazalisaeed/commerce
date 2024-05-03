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
from . import util # above this i have imported all the stuff I need for backend
#util is contains a utility which makes the listing data usable in the template with bids

def index(request): # landing page of  my website shows all the listings
    all_the_listings = listing.objects.order_by('-timestamp').prefetch_related('bid')
    listing_data_with_bids = util.display_listing(all_the_listings,False)
    return render(request, "auctions/index.html",{"listings":listing_data_with_bids})

def login_view(request): # makes the user loging by checking password username writed by cs50
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
    
@login_required(login_url='/login')
def create_listing(request): # let user creat a new listing
    if request.method =="POST":
        form = new_listing_form(request.POST)
        if form.is_valid(): # checks if the submitted data for a listing if valid
            user_instance = User.objects.get(username= request.user.username) 
            new_listing = listing(user = user_instance,title = form.cleaned_data["title"], description = form.cleaned_data["description"], image_url = form.cleaned_data["image_url"], category = form.cleaned_data["category"], is_auction_active = "True")
            new_listing.save() # saving a listing entry 
            initial_bid = all_bids(user = user_instance , bid = form.cleaned_data["initial_bid"], for_which_listing = new_listing)
            initial_bid.save() # saving the initial bid for this listing
            return HttpResponseRedirect(reverse("index")) # takes them back to the index page to show listing is there
        else:
            return render(request, "auctions/new_listing.html",{"form": new_listing_form()})
    else:
        return render(request, "auctions/new_listing.html",{"form": new_listing_form()})
    

def listing_page(request, listing_id): # displays all the individual data of the listing and the comments
    
    if request.method =="POST":
        try:
            # fist half of this function deal with the lastest bid that is posted by the user 

            user_instance = User.objects.get(username= request.user.username) 
            form = biding_form(request.POST)
            if form.is_valid(): # checks if the bid is higher then the last bid placed
                this_listing = listing.objects.get(pk = listing_id)
                current_bid = all_bids(user = user_instance, bid = form.cleaned_data["current_bid"], for_which_listing = this_listing)
                current_bid.save() # saves the lastest bid
                return HttpResponseRedirect(reverse("listing_page", args=[listing_id])) 
        
            else: # if the bid is not valid user is presendted is a error message that the bid was lower then the previous bid
                which_listing = listing.objects.get(pk = listing_id)
                lastbid = which_listing.bid.filter(for_which_listing = listing_id).order_by('-bid').first()
                messages.info(request, f"There was an error. your bid must be greater then ${lastbid}")
                return HttpResponseRedirect(reverse("listing_page", args=[listing_id])) 
        except ObjectDoesNotExist:
            return render(request, "auctions/error_page.html",{"error":"user must be signed in"}) # user must be sign in to palce this bid            
    else:

        
        try: # second half of the function manages the comments,bid history and  wishlist
            is_this_in_wishlist = False # this is a non standard method to redirect either to listing page or controll center.
            which_listing = listing.objects.get(pk = listing_id)  # the querry to the data base
            and_its_bid = which_listing.bid.order_by('-bid').first()
            all_the_bids = all_bids.objects.all().filter(for_which_listing = listing_id).order_by('-bid')
            comments_for_this_listing = comments.objects.all().filter(for_which_listing = listing_id).order_by('-timestamp')
            if  User.objects.filter(username= request.user.username).exists():
                
                if wishlist.objects.filter(user = User.objects.get(username= request.user.username), for_which_listing = listing_id).exists(): 
                    is_this_in_wishlist = True
                else:
                    is_this_in_wishlist = False
        
            if comments_for_this_listing.exists(): #decided if there are zero comments in the data base
                all_comments = comments_for_this_listing
                total_comments = comments.objects.all().filter(for_which_listing = listing_id).count()
            else:
                all_comments = "wow such empty"
                total_comments = 0    
            bid_form = biding_form(initial ={'listing_id':listing_id}) # set initial vlaue of comments and bid for procees in other fuctions like comments wishlist or closing the auction
            hidden_listing_id_form = listing_id_form(initial ={'hidden_listing_id':listing_id})
            return render(request, "auctions/listing_page.html",{ "listing": which_listing, "bid": and_its_bid, "bid_histroy": all_the_bids, "bid_form":bid_form,"comments_form":comments_form, "hidden_listing_id":hidden_listing_id_form, "comment_section":all_comments,"total_comments":total_comments,"is_this_in_wishlist": is_this_in_wishlist})
    
        except ObjectDoesNotExist:
            return render(request, "auctions/error_page.html",{"error":"no listing found with this url try again"})
        

@login_required(login_url='/login') # add new comments to the data base    
def comment_section(request):
    if request.method =="POST":
        form = comments_form(request.POST)
        id_form = listing_id_form(request.POST)
        if form.is_valid() and id_form.is_valid():
            user_instance = User.objects.get(username= request.user.username) 
            this_listing = listing.objects.get(pk = id_form.cleaned_data["hidden_listing_id"]) 
            new_comment = comments(user = user_instance, comment = form.cleaned_data["comment"], for_which_listing = this_listing) # this is the main querry that save the content of the comments
            new_comment.save()
            return HttpResponseRedirect(reverse("listing_page", args=[id_form.cleaned_data["hidden_listing_id"]])) # redirect user back to the listing page with arg being the id of the list so the listing_page function knows which page to load
    

@login_required(login_url='/login')
def wishlistfunction(request): # this function add the listing to the wishllist to the user
    user_instance = User.objects.get(username= request.user.username)
    if request.method =="POST":
        try:
            id_form = listing_id_form(request.POST)
            if id_form.is_valid():
                if wishlist.objects.filter(user = user_instance).exists(): # cause this is a many to many relation ship instead of makiing a new relation for each user thus it instead add a new item to an exsitsting wihslist
                    add_to_wishlist = wishlist.objects.get(user = user_instance) 
                    add_to_wishlist.for_which_listing.add(id_form.cleaned_data["hidden_listing_id"])
                    messages.success(request, 'this item added to your wishlist')
                    return HttpResponseRedirect(reverse("listing_page", args=[id_form.cleaned_data["hidden_listing_id"]]))
                else:    
                    new_wish_list_item = wishlist() # else this instead makes a new entry if the user dose not exist 
                    new_wish_list_item.save()
                    new_wish_list_item.user.set([user_instance])
                    new_wish_list_item.for_which_listing.set([id_form.cleaned_data["hidden_listing_id"]]) # and then save the listing in there  wishlist
                    messages.success(request, 'this item added to your wishlist')
                return HttpResponseRedirect(reverse("listing_page", args=[id_form.cleaned_data["hidden_listing_id"]]))
        except ObjectDoesNotExist:
            return render(request, "auctions/error_page.html",{"error":"no listing found with this url try again"})
    else: # if request metod is get then it shows that user his/her all the listing on the wishlist page
        all_wishlist_items = wishlist.objects.all().filter(user = user_instance).order_by('-timestamp')
        wishlish_data_with_bids = []
        for each_item in all_wishlist_items:
            wishlish_data_with_bids.extend(util.display_listing(each_item,True))    
        return render(request, "auctions/wishlist.html",{"wishlist":wishlish_data_with_bids})

def delwislist(request): # dlelte items in the wishlist 
    if request.method =="POST":
        user_instance = User.objects.get(username= request.user.username)
        listing_id = listing.objects.get(pk = request.POST['wishlist_id']) # check which item is requested to be deleted
        which_page = request.POST['which_page']
        print(type(which_page))
        delete_wishlist_item = wishlist.objects.get(user = user_instance, for_which_listing = listing_id)
        if delete_wishlist_item.for_which_listing.count() == 1: # chekc is this is the last item in there wislist this delete the relation ship in the data bade
            delete_wishlist_item.delete()
            if which_page == 'True':
                messages.info(request, 'this item deleted from your wishlist')
                return HttpResponseRedirect(reverse("listing_page", args=[request.POST['wishlist_id']]))
            else:
                
                return HttpResponseRedirect(reverse('wishlist'))
        else:
            delete_wishlist_item.for_which_listing.remove(listing_id) # if this  is not last  item in their wihslist therfoure, it only removes the item but keeps the relationship

            if which_page == 'True':
                messages.info(request, 'this item deleted from your wishlist')
                return HttpResponseRedirect(reverse("listing_page", args=[request.POST['wishlist_id']]))
            else:
                return HttpResponseRedirect(reverse('wishlist'))
    else:
        return render(request, "auctions/error_page.html",{"error":"NO Entry"})

def categories(request): # redirect user  to the items in the that category
    if request.method =="POST":
        which_catagory = request.POST["category_name"]
        category_item = listing.objects.all().filter(category = which_catagory).prefetch_related('bid').order_by('-timestamp') # the querry  which request that items of that category which is requested
        listing_data_with_bids = util.display_listing(category_item,False)
        return render(request, "auctions/index.html",{"listings":listing_data_with_bids})
        
    else: # if the reqest method is post this instead  show user all the aviabel catgories
        all_categories = listing.objects.values('category').annotate(total=Count('category')).filter(is_auction_active=True) 
        return render(request, "auctions/categories.html",{"all_categories":all_categories})
    
def close_auction(request): # closes the listing which is only requested by the owner of the listing
    if request.method =="POST": 
        id_form = request.POST["hidden_id"]
        closeing_auction = listing.objects.get(pk = id_form)
        winning_bidder = closeing_auction.bid.order_by('-bid').first()
        which_page = request.POST['which_page'] # non standard method of redireting  user either to listing page or controll center
        closeing_auction.is_auction_active = False
        closeing_auction.save()    
        messages.success(request, f'this listing has been cloed and the winning bidder is {winning_bidder.user}')
        if which_page == 'True':
            return HttpResponseRedirect(reverse("listing_page", args=[request.POST["hidden_id"]]))
        else:
            return HttpResponseRedirect(reverse("HQ"))
            

def delete_auction(request): #addiotioanl feature not recommend by cs50  you can also delete the lsiting either with or without closing it first 
    if request.method =="POST":
        id_form = request.POST["hidden_id"]
        deleteing_auction = listing.objects.get(pk = id_form)
        deleteing_auction.delete()
        messages.success(request, 'this listing has been been Deleted')
        return HttpResponseRedirect(reverse("HQ"))

@login_required(login_url='/login')
def controll(request): # additional feature this fuction list one  user all listing they have put up for auction
    user_instance = User.objects.get(username= request.user.username)

    if listing.objects.filter(user = user_instance).exists() == False:
        return render(request, "auctions/error_page.html",{"error": "you have not posted any listing for acution"})
    else:
        user_listings = listing.objects.filter(user = user_instance).order_by('-timestamp').prefetch_related('bid')
        listing_data_with_bids = util.display_listing(user_listings,False)
    
        return render(request, "auctions/controll_center.html",{"listings":listing_data_with_bids})

def delete_comment(request): # only let user whos comments it is to let them delete if they want 
    id_form = request.POST["comment_id"]
    deleteing_comment = comments.objects.get(pk = id_form)
    listing_id =  deleteing_comment.for_which_listing.id
    deleteing_comment.delete()
    messages.success(request, 'Your Comment deleted successfuly')
    return HttpResponseRedirect(reverse("listing_page", args=[listing_id]))


