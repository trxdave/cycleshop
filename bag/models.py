from django.db import models
from products.models import Product
from checkout.models import Order
from django.contrib.auth.models import User

class Order(models.Model):
    """ Model representing an order """
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='bag_orders'
    )
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    street_address1 = models.CharField(max_length=80)
    street_address2 = models.CharField(max_length=80, blank=True)
    town_or_city = models.CharField(max_length=40)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=40)
    county = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} by {self.full_name}"

    def get_total_order_price(self):
        return sum(item.get_total_price() for item in self.bag_items.all())

class BagItem(models.Model):
    order = models.ForeignKey(Order, related_name='bag_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.product.price