# Generated by Django 4.2.7 on 2024-04-12 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0022_rename_for_which_lsiting_wishlist_for_which_listing'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='catagorie',
            new_name='category',
        ),
    ]
