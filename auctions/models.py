from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator



class User(AbstractUser): #user table 
    pass

class listing(models.Model):  # a table for listing
    user = models.ForeignKey("User", on_delete = models.PROTECT)
    title = models.CharField(max_length = 80)
    description = models.TextField(max_length= 10000, blank = True)
    timestamp = models.DateTimeField(auto_now_add = True , null = True)
    image_url = models.URLField()
    def __str__ (self):
        return(f" {self.title},{self.id}")

class all_bids(models.Model): # a table to store bids
    user = models.ForeignKey("User", on_delete = models.PROTECT, null = True)
    bid = models.FloatField(MinValueValidator(0))
    timestamp = models.DateTimeField(auto_now_add = True , null = True)
    for_which_listing = models.ForeignKey("listing",on_delete = models.CASCADE, related_name = 'bid', null = True)
    def __str__(self):
        return str(self.bid)   

class comments(models.Model): # a table for comments
    user = models.ForeignKey("User", on_delete = models.PROTECT, null = True)
    comment = models.TextField(max_length = 10000, blank = True)
    timestamp = models.DateTimeField(auto_now_add = True , null = True)
    for_which_listing = models.ForeignKey("listing",on_delete = models.CASCADE, related_name = 'comment', null = True)
class wishlist(models.Model): # a table for wishlist of users
    user =  models.ManyToManyField(User)
    for_which_lsiting = models.ManyToManyField(listing)
    timestamp = models.DateTimeField(auto_now_add = True , null = True)
    
