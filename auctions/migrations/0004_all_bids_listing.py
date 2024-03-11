# Generated by Django 4.2.7 on 2024-03-10 17:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_comments_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='all_bids',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='listing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Title', models.CharField(max_length=80)),
                ('discription', models.TextField(blank=True, max_length=10000)),
                ('image_url', models.URLField()),
                ('bid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auctions.all_bids')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
