# Generated by Django 4.2.7 on 2024-04-11 18:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0021_listing_catagorie_alter_listing_title_wishlist'),
    ]

    operations = [
        migrations.RenameField(
            model_name='wishlist',
            old_name='for_which_lsiting',
            new_name='for_which_listing',
        ),
    ]