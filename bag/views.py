from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product
from django.contrib import messages

# View to display the user's shopping bag
def view_bag(request):
    """ A view to display the user's shopping bag """
    bag = request.session.get('bag', {})
    total = sum(item['price'] * item['quantity'] for item in bag.values())
    bag_items_count = sum(item['quantity'] for item in bag.values())

    context = {
        'bag': bag,
        'total': total,
        'bag_items_count': bag_items_count,
    }
    return render(request, 'bag/bag.html', context)


# View to add a product to the shopping bag
def add_to_bag(request, product_id):
    """ A View to add a product to the shopping bag """
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        messages.error(request, 'Quantity must be a positive number.')
        return redirect('bag:view_bag')

    bag = request.session.get('bag', {})

    if str(product_id) in bag:
        bag[str(product_id)]['quantity'] += quantity
        messages.info(request, f"Updated {product.name} quantity in your bag.")
    else:
        bag[str(product_id)] = {'price': float(product.price), 'quantity': quantity}
        messages.success(request, f"Added {product.name} to your bag.")

    request.session['bag'] = bag
    return redirect('bag:view_bag')


def update_quantity(request, product_id):
    """A view to update the quantity of a specific item in the bag"""
    quantity = int(request.POST.get('quantity'))

    if quantity <= 0:
        messages.error(request, 'Quantity must be a positive number.')
        return redirect('bag:view_bag')
        
    bag = request.session.get('bag', {})

    if str(product_id) in bag:
        if quantity > 0:
            bag[str(product_id)]['quantity'] = quantity
        else:
            del bag[str(product_id)]

    request.session['bag'] = bag
    return redirect('bag:view_bag')


def checkout(request):
    """ View to handle the checkout process """
    return render(request, 'checkout/checkout.html')


def remove_from_bag(request, product_id):
    """A view to remove a product from the shopping bag"""
    bag = request.session.get('bag', {})
    product = get_object_or_404(Product, id=product_id)

    if str(product_id) in bag:
        del bag[str(product_id)]
        request.session['bag'] = bag
        messages.success(request, f"{product.name} removed from your bag.")
    else:
        messages.warning(request, "Product not found in your bag.")

    return redirect('bag:view_bag')