# Generated by Django 5.1.1 on 2024-10-24 09:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cycleshop', '0002_newslettersubscriber'),
        ('products', '0005_product_rating_count_product_total_ratings'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='wishlist',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.wishlist'),
        ),
    ]
