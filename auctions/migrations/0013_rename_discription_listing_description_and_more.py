# Generated by Django 4.2.7 on 2024-03-14 14:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_rename_title_listing_title'),
    ]

    operations = [
        migrations.RenameField(
            model_name='listing',
            old_name='discription',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='listing',
            old_name='intial_bid',
            new_name='initial_bid',
        ),
    ]
