from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


def product_category(request, category):
    category_obj = get_object_or_404(Category, name=category)
    products = Product.objects.filter(category=category)
    return render(request, 'products/product_list.html', {'products': products, 'category': category})