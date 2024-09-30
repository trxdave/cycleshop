from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Wishlist
from products.models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})


def product_category(request, category):
    category_obj = get_object_or_404(Category, slug=category)
    products = Product.objects.filter(category=category_obj)
    return render(request, 'products/product_list.html', {'products': products, 'category': category_obj.name})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})


@login_required
def add_product(request):
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('products:product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('products:product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'product': product,
    }

    return render(request, template, context)


@login_required
def delete_product(request, product_id):
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products:product_list'))


def road_bikes(request):
    products = Product.objects.filter(category__name='Road Bikes')
    return render(request, 'products/category_products.html', {'products': products, 'category_name': 'Road Bikes'})


def mountain_bikes(request):
    products = Product.objects.filter(category__name='Mountain Bikes')
    return render(request, 'products/category_products.html', {'products': products, 'category_name': 'Mountain Bikes'})


def electric_bikes(request):
    products = Product.objects.filter(category__name='Electric Bikes')
    return render(request, 'products/category_products.html', {'products': products, 'category_name': 'Electric Bikes'})


def kids_bikes(request):
    products = Product.objects.filter(category__name='Kids Bikes')
    return render(request, 'products/category_products.html', {'products': products, 'category_name': 'Kids Bikes'})


def clothing(request):
    products = Product.objects.filter(category__name='Clothing')
    return render(request, 'products/category_products.html', {'products': products, 'category_name': 'Clothing'})


def accessories(request):
    products = Product.objects.filter(category__name='Accessories')
    return render(request, 'products/category_products.html', {'products': products, 'category_name': 'Accessories'})


@login_required
def view_wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'products/wishlist.html', {'wishlist': wishlist})


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    if product in wishlist.products.all():
        messages.info(request, "Product already in wishlist.")
    else:
        wishlist.products.add(product)
        messages.success(request, "Product added to wishlist.")

    return redirect('products:product_detail', product_id=product_id)


@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)

    if product in wishlist.products.all():
        wishlist.products.remove(product)
        messages.success(request, "Product removed from wishlist.")
    else:
        messages.info(request, "Product was not in your wishlist.")

    return redirect('products:view_wishlist')