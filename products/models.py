from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    sku = models.CharField(max_length=50, unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    image_url = models.URLField(max_length=1024, null=True, blank=True)

    def __str__(self):
        return self.name