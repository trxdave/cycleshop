from django.db import models

# Create your models here.
class BagItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()