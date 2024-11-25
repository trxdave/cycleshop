from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Order(models.Model):
    """Model representing an order."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default='pending'
    )

    def __str__(self):
        return f"Order {self.id} - {self.full_name}"

    def get_total_order_price(self):
        return sum(item.get_total_price() for item in self.bag_items.all())
