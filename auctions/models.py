from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator



class User(AbstractUser): #user table 
    pass

class listing(models.Model):  # a table for listing
    user = models.ForeignKey("User", on_delete = models.PROTECT)
    title = models.CharField(max_length = 80)
    discription = models.TextField(max_length= 10000, blank = True)
    timestamp = models.DateTimeField(auto_now_add = True , null = True)
    image_url = models.URLField()
    intial_bid = models.FloatField(validators = [MinValueValidator(0)], null = True)

class all_bids(models.Model): # a table to store bids
    user = models.ForeignKey("User", on_delete = models.PROTECT, null = True)
    bid = models.FloatField(MinValueValidator(0))
    timestamp = models.DateTimeField(auto_now_add = True , null = True)
    listing = models.ForeignKey("listing",on_delete = models.CASCADE, null = True)    

class comments(models.Model): # a table for comments
    user = models.ForeignKey("User", on_delete = models.PROTECT, null = True)
    comment = models.TextField(max_length = 10000, blank = True)
    timestamp = models.DateTimeField(auto_now_add = True , null = True)
    
