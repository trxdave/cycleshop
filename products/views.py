from django.shortcuts import render
from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


def product_category(request, category):
    products = Product.objects.filter(category=category)
    return render(request, 'products/product_list.html', {'products': products, 'category': category})