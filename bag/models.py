from django.db import models
from products.models import Product

# Create your models here.
class BagItem(models.Model):
    """ Model representing an item in the user's shopping bag """
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.product.price