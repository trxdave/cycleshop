from django.db import models
from django.contrib.auth.models import User

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
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        """ String representation of the Product model, returns the name of the product """
        return self.name


class Wishlist(models.Model):
    """ Model representing a user's wishlist """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        """ String representation of the Wishlist model, returns the user's wishlist """
        return f"{self.user.username}'s Wishlist"