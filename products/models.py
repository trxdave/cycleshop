from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

# Create your models here.

class Category(models.Model):
    """ Model representing a product category """
    name = models.CharField(max_length=200, unique=True)
    description = models. TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        """ Automatically generate a slug based on the category name if not provided """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        """ String representation of the Category model, returns the name of the category """
        return self.name

class Product(models.Model):
    """ Model representing a product """
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    sku = models.CharField(max_length=50, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def update_rating(self, new_rating):
        """ Update the average rating when a new rating is submitted """
        self.total_ratings += new_rating
        self.rating_count += 1
        self.rating = self.total_ratings / self.rating_count
        self.save()

    def __str__(self):
        return self.name


class Wishlist(models.Model):
    """ Model representing a user's wishlist """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        """ String representation of the Wishlist model, returns the user's wishlist """
        return f"{self.user.username}'s Wishlist"