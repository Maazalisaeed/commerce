# Generated by Django 4.2.7 on 2024-03-16 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0014_rename_listing_all_bids_for_which_lisitng'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='all_bids',
            name='for_which_lisitng',
        ),
        migrations.AddField(
            model_name='all_bids',
            name='for_wh_lisitng',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='auctions.listing'),
        ),
    ]
