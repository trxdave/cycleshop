from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from cloudinary.models import CloudinaryField


class Category(models.Model):
    """Model representing a product category."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        """Automatically a slug based on the category name if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        """String representation of the Category model."""
        return self.name


class Product(models.Model):
    """Model representing a product."""
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    sku = models.CharField(max_length=50, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_ratings = models.IntegerField(default=0)
    rating_count = models.IntegerField(default=0)
    image = CloudinaryField('image', null=True, blank=True)
    category = models.ForeignKey(
        'Category', on_delete=models.CASCADE, related_name='products'
    )

    def update_rating(self):
        """Recalculate and update the average rating."""
        ratings = self.ratings.all()
        if ratings.exists():
            self.rating = sum(r.rating for r in ratings) / ratings.count()
            self.rating_count = ratings.count()
        else:
            self.rating = 0
            self.rating_count = 0
        self.save()

    def __str__(self):
        return self.name


class Wishlist(models.Model):
    """Model representing a user's wishlist."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)

    def __str__(self):
        """String representation of the Wishlist model."""
        return f"{self.user.username}'s Wishlist"


class Rating(models.Model):
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='ratings',
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # e.g., 1 to 5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user')

    def __str__(self):
        return (
            f"Rating {self.rating} "
            f"for {self.product.name} "
            f"by {self.user.username}"
        )
