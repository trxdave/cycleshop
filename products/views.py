from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Wishlist
from products.models import Product
from .forms import ProductForm


def product_list(request):
    """ A view to return the list of all products """
    products = Product.objects.all()
    return render(
        request, 'products/product_list.html', {'products': products}
    )


def product_category(request, category):
    """ A view to return products filtered by category """
    category_obj = get_object_or_404(Category, slug=category)
    products = Product.objects.filter(category=category_obj)
    return render(
        request, 'products/product_list.html', {
            'products': products,
            'category': category_obj.name,
        })


def product_detail(request, product_id):
    """ A view to return the details of a single product """
    product = get_object_or_404(Product, id=product_id)
    return render(
        request, 'products/product_detail.html', {'product': product}
    )


@login_required
def manage_products(request):
    """ A view to manage all products """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can access this page.')
        return redirect('home')

    products = Product.objects.all()
    return render(request, 'products/manage_products.html', {'products': products})


@login_required
def add_product(request):
    """ A view to add a new product, accessible only to superusers """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(
                reverse('products:product_detail', args=[product.id])
            )
        else:
            messages.error(
                request,
                'Failed to add product. Please ensure the form is valid.'
            )
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """ A view to edit an existing product, accessible only to superusers """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(
            request.POST, request.FILES, instance=product
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(
                reverse('products:product_detail', args=[product.id])
            )
        else:
            messages.error(
                request,
                'Failed to update product. Please ensure the form is valid.'
            )
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
    """ A view to delete a product, accessible only to superusers """
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product deleted!')
    return redirect(reverse('products:product_list'))


def road_bikes(request):
    """ A view to return all Road Bikes products """
    products = Product.objects.filter(category__name='Road Bikes')
    return render(
        request,
        'products/category_products.html',
        {'products': products, 'category_name': 'Road Bikes'}
    )


def mountain_bikes(request):
    """ A view to return all Mountain Bikes products """
    products = Product.objects.filter(category__name='Mountain Bikes')
    return render(
        request,
        'products/category_products.html',
        {'products': products, 'category_name': 'Mountain Bikes'}
    )


def electric_bikes(request):
    """ A view to return all Electric Bikes products """
    products = Product.objects.filter(category__name='Electric Bikes')
    return render(
        request,
        'products/category_products.html',
        {'products': products, 'category_name': 'Electric Bikes'}
    )


def kids_bikes(request):
    """ A view to return all Kids Bikes products """
    products = Product.objects.filter(category__name='Kids Bikes')
    return render(
        request,
        'products/category_products.html',
        {'products': products, 'category_name': 'Kids Bikes'}
    )


def clothing(request):
    """ A view to return all Clothing products """
    products = Product.objects.filter(category__name='Clothing')
    return render(
        request,
        'products/category_products.html',
        {'products': products, 'category_name': 'Clothing'}
    )


def accessories(request):
    """ A view to return all Accessories products """
    products = Product.objects.filter(category__name='Accessories')
    return render(
        request,
        'products/category_products.html',
        {'products': products, 'category_name': 'Accessories'}
    )


def faq(request):
    """ A view to return the FAQ page """
    return render(request, 'products/faq.html')


def return_exchange(request):
    """ A view to return the Return & Exchanges page """
    return render(request, 'customer_services/return_exchange.html')


def shipping_information(request):
    """ A view to return the Shipping Information page """
    return render(request, 'customer_services/shipping_information.html')


@login_required
def view_wishlist(request):
    """ A view to return the user's wishlist """
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'products/wishlist.html', {'wishlist': wishlist})


@login_required
def add_to_wishlist(request, product_id):
    """ A view to add a product to the user's wishlist """
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
    """ A view to remove a product from the user's wishlist """
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)

    if product in wishlist.products.all():
        wishlist.products.remove(product)
        messages.success(request, "Product removed from wishlist.")
    else:
        messages.info(request, "Product was not in your wishlist.")

    return redirect('products:view_wishlist')