from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listings", views.create_listing, name="create_listing"),
    path("<int:listing_id>", views.listing_page, name="listing_page"),
    path("comments", views.comment_section, name="comment_section"),
    path("wishlist", views.wishlistfunction, name="wishlist"),
]
