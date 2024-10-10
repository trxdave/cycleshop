from django.shortcuts import render

# Create your views here.
def view_bag(request):
    """ A view to display the user's shopping bag """
    bag = request.session.get('bag', {})
    total = sum(item['price'] * item['quantity'] for item in bag.values())
    
    context = {
        'bag': bag,
        'total': total,
    }
    return render(request, 'bag/bag.html', context)


def add_to_bag(request, product_id):
    """ A View to add a product to the shopping bag """
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    bag = request.session.get('bag', {})
    if product_id in bag:
        bag[product_id]['quantity'] += quantity
    else:
        bag[product_id] = {'price': float(product.price), 'quantity': quantity}

    request.session['bag'] = bag
    return redirect('view_bag')


def remove_from_bag(request, product_id):
    """ A view to remove a product from the shopping bag """
    bag = request.session.get('bag', {})
    if product_id in bag:
        del bag[product_id]
        request.session['bag'] = bag
    return redirect('view_bag')