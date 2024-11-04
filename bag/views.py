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
    bag = request.session.get('bag', {})
    bag_items = []
    total = 0
    bag_items_count = 0

    # Calculate the subtotal, total, and item count
    for product_id, item in bag.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = item['price'] * item['quantity']
        total += subtotal
        bag_items_count += item['quantity']
        bag_items.append({
            'product': product,
            'price': item['price'],
            'quantity': item['quantity'],
            'subtotal': subtotal,
        })

    # Calculate delivery
    delivery = 0 if total >= settings.FREE_DELIVERY_THRESHOLD else total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
    grand_total = total + delivery

    # Store the total price in the session for Stripe payments
    request.session['total_price'] = total

    context = {
        'bag': bag_items,
        'total': number_format(total, decimal_pos=2, use_l10n=True),
        'delivery': number_format(delivery, decimal_pos=2, use_l10n=True),
        'grand_total': number_format(grand_total, decimal_pos=2, use_l10n=True),
        'bag_items_count': bag_items_count,
    }

    return render(request, 'bag/bag.html', context)

# View to add a product to the shopping bag
def add_to_bag(request, product_id):
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

# View to update the quantity of a specific item in the bag
def update_quantity(request, product_id):
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

# View to handle the checkout process
def checkout(request):
    bag = request.session.get('bag', {})
    total = sum(item['price'] * item['quantity'] for item in bag.values())
    delivery = 0 if total >= settings.FREE_DELIVERY_THRESHOLD else total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
    grand_total = int((total + delivery) * 100)

    # Create Stripe PaymentIntent
    intent = stripe.PaymentIntent.create(
        amount=grand_total,
        currency=settings.STRIPE_CURRENCY,
    )

    form = OrderForm()

    context = {
        'form': form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': intent.client_secret,
        'total': number_format(total, decimal_pos=2, use_l10n=True),
        'delivery': number_format(delivery, decimal_pos=2, use_l10n=True),
        'grand_total': number_format(grand_total / 100, decimal_pos=2, use_l10n=True),
    }

    return render(request, 'checkout/checkout.html', context)

# View to remove a product from the shopping bag
def remove_from_bag(request, product_id):
    bag = request.session.get('bag', {})
    product = get_object_or_404(Product, id=product_id)

    if str(product_id) in bag:
        del bag[str(product_id)]
        messages.success(request, f"{product.name} removed from your bag.")
    else:
        messages.warning(request, "Product not found in your bag.")

    request.session['bag'] = bag
    return redirect('bag:view_bag')

# View to create a Stripe checkout session
@require_POST
def create_checkout_session(request):
    try:
        bag = request.session.get('bag', {})
        total = sum(item['price'] * item['quantity'] for item in bag.values())
        delivery = 0 if total >= settings.FREE_DELIVERY_THRESHOLD else total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        grand_total = int((total + delivery) * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': settings.STRIPE_CURRENCY,
                    'product_data': {'name': 'Total Order'},
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



def checkout_view(request):
    # Get the bag from the session
    bag = request.session.get('bag', {})
    
    # Calculate total and delivery
    total = sum(item['price'] * item['quantity'] for item in bag.values())
    delivery = 0 if total >= settings.FREE_DELIVERY_THRESHOLD else total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
    grand_total = total + delivery

    # Convert the total to cents for Stripe (since Stripe uses the smallest currency unit)
    grand_total_cents = int(grand_total * 100)

    # Create a PaymentIntent
    intent = stripe.PaymentIntent.create(
        amount=grand_total_cents,
        currency=settings.STRIPE_CURRENCY,
    )

    # Pass the client secret to the template
    context = {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': intent.client_secret,
        'bag_items': bag,  # Pass your bag items for display
        'total': total,
        'delivery': delivery,
        'grand_total': grand_total,
    }

    return render(request, 'checkout/checkout.html', context)