# Generated by Django 4.2.7 on 2024-03-10 19:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_comments_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='bid',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='auctions.all_bids'),
        ),
    ]
