def display_listing(queryset):
    listing_data_with_bids=[]
    for each_listing in queryset:
        data_of_each_listing = {
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