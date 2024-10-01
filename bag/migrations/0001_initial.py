# Generated by Django 5.1.1 on 2024-10-01 10:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0004_category_slug_wishlist'),
    ]

    operations = [
        migrations.CreateModel(
            name='BagItem',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('quantity', models.IntegerField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
        ),
    ]
