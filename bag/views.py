from django.shortcuts import render, get_object_or_404, redirect
from products.models import Product
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import stripe
from django.utils.formats import number_format
from django.views.decorators.http import require_POST
from .forms import OrderForm

stripe.api_key = settings.STRIPE_SECRET_KEY

# View to display the user's shopping bag
def view_bag(request):
    """ A view to display the user's shopping bag """
    bag = request.session.get('bag', {})
    total = sum(item['price'] * item['quantity'] for item in bag.values())
    bag_items_count = sum(item['quantity'] for item in bag.values())

    if total >= settings.FREE_DELIVERY_THRESHOLD:
        delivery = 0
    else:
        delivery = settings.STANDARD_DELIVERY_PERCENTAGE

    grand_total = total + delivery

    # Format total and grand_total with commas
    formatted_total = number_format(total, decimal_pos=2, use_l10n=True)
    formatted_grand_total = number_format(grand_total, decimal_pos=2, use_l10n=True)

    context = {
        'bag': bag,
        'total': formatted_total,
        'delivery': delivery,
        'grand_total': formatted_grand_total,
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
    # Calculate total and delivery based on bag contents
    bag = request.session.get('bag', {})
    total = sum(item['price'] * item['quantity'] for item in bag.values())
    
    # Apply delivery fee if total is below the free delivery threshold
    if total >= settings.FREE_DELIVERY_THRESHOLD:
        delivery = 0
    else:
        delivery = settings.STANDARD_DELIVERY_PERCENTAGE

    # Calculate the grand total and convert to cents for Stripe
    grand_total = int((total + delivery) * 100)

    # Create Stripe payment intent
    intent = stripe.PaymentIntent.create(
        amount=grand_total,
        currency=settings.STRIPE_CURRENCY,
    )

    form = OrderForm()
    
    context = {
        'form': form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': intent.client_secret,
        'total': total,
        'delivery': delivery,
        'grand_total': grand_total / 100,
    }
    
    return render(request, 'checkout/checkout.html', context)


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



def calculate_order_total(request):
    bag = request.session.get('bag', {})
    total = sum(item['price'] * item['quantity'] for item in bag.values())

    if total >= settings.FREE_DELIVERY_THRESHOLD:
        delivery = 0
    else:
        delivery = settings.STANDARD_DELIVERY_PERCENTAGE

    grand_total = total + delivery
    return int(grand_total * 100)



@require_POST
def create_checkout_session(request):
    try:
        # Retrieve the bag and calculate total, delivery, and grand total
        bag = request.session.get('bag', {})
        total = sum(item['price'] * item['quantity'] for item in bag.values())
        delivery = settings.STANDARD_DELIVERY_PERCENTAGE if total < settings.FREE_DELIVERY_THRESHOLD else 0
        grand_total = int((total + delivery) * 100)  # Convert to cents

        # Create the Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': settings.STRIPE_CURRENCY,
                    'product_data': {
                        'name': 'Total Order',
                    },
                    'unit_amount': grand_total,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/success/'),
            cancel_url=request.build_absolute_uri('/cancel/'),
        )

        return JsonResponse({'sessionId': session.id})
        
    except Exception as e:
        return JsonResponse({'error': str(e)})