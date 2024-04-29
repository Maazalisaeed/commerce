import re

def sub_display(each_listing,listing_data_with_bids):  # use the list given as the argument to make dictionaries of the different listings 
    data_of_each_listing = {
        'user': each_listing.user,
        'title': each_listing.title,
        'listing_id': each_listing.pk,
        'image_url': each_listing.image_url,
        'description': each_listing.description,
        'timestamp': each_listing.timestamp,
        'bid': each_listing.bid.filter(for_which_listing = each_listing.id).order_by('-bid').first(),
        'is_auction_active': each_listing.is_auction_active,
        'category': each_listing.category}
    listing_data_with_bids.append(data_of_each_listing)
    return listing_data_with_bids


def display_listing(queryset,data_type): # this is main function that converts the queryset into a list of dictionary for the template to digest cause in template I can not make complecated querry request 
    if data_type == True:
        listing_data_with_bids=[]
        for each_listing in queryset.for_which_listing.all(): # this is main difference in manytomany i have to call.for_which_listing.all() to actualy request for the data of  the data set mainly used in wishlist
            listing_with_bids = sub_display(each_listing,listing_data_with_bids) # these two if and else 
            # call the sub_diplay function individualy depending of either it is many to many or foreign key
        return listing_with_bids
    else:
        listing_data_with_bids=[] # this is ther other part of the fuction mainly use in the rest of the application
        for each_listing in queryset:
            listing_with_bids = sub_display(each_listing,listing_data_with_bids)  
        return listing_with_bids

