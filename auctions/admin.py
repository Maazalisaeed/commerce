from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.User)
admin.site.register(models.comments)
admin.site.register(models.listing)
admin.site.register(models.all_bids)