from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.utils.formats import number_format
from django.views.decorators.http import require_POST
from products.models import Product
from checkout.forms import OrderForm
import stripe

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


# Helper functions
def calculate_delivery(total):
    """Calculate delivery based on the total."""
    if total >= settings.FREE_DELIVERY_THRESHOLD:
        return 0
    return total * settings.STANDARD_DELIVERY_PERCENTAGE / 100


def calculate_totals(bag):
    """Calculate the total, delivery, and grand total for the bag."""
    total = sum(
        item['price'] * item['quantity']
        for item in bag.values()
    )
    delivery = calculate_delivery(total)
    grand_total = total + delivery
    return total, delivery, grand_total


def get_bag(request):
    """Get the bag from the session."""
    return request.session.get('bag', {})


def save_bag(request, bag):
    """Save the bag back to the session."""
    request.session['bag'] = bag


# Bag-related views
def view_bag(request):
    """View to display the user's shopping bag."""
    bag = get_bag(request)
    total, delivery, grand_total = calculate_totals(bag)
    bag_items_count = sum(item['quantity'] for item in bag.values())
    bag_items = []

    for product_id, item in bag.items():
        product = get_object_or_404(Product, id=product_id)
        bag_items.append({
            'product': product,
            'price': item['price'],
            'quantity': item['quantity'],
            'subtotal': item['price'] * item['quantity'],
        })

    context = {
        'bag': bag_items,
        'total': number_format(
            total, decimal_pos=2, use_l10n=True
        ),
        'delivery': number_format(
            delivery, decimal_pos=2, use_l10n=True
        ),
        'grand_total': number_format(
            grand_total, decimal_pos=2, use_l10n=True
        ),
        'bag_items_count': bag_items_count,
    }
    return render(request, 'bag/bag.html', context)


def add_to_bag(request, product_id):
    """View to add a product to the shopping bag."""
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    bag = get_bag(request)

    if str(product_id) in bag:
        bag[str(product_id)]['quantity'] += quantity
        messages.info(
            request,
            f"Updated {product.name} quantity in your bag."
        )
    else:
        bag[str(product_id)] = {
            'price': float(product.price),
            'quantity': quantity,
        }
        messages.success(
            request,
            f"Added {product.name} to your bag."
        )

    save_bag(request, bag)
    return redirect('bag:view_bag')


def remove_from_bag(request, product_id):
    """View to remove a product from the shopping bag."""
    bag = get_bag(request)
    product = get_object_or_404(Product, id=product_id)

    if str(product_id) in bag:
        del bag[str(product_id)]
        messages.success(
            request,
            f"{product.name} removed from your bag."
        )
    else:
        messages.warning(
            request,
            "Product not found in your bag."
        )

    save_bag(request, bag)
    return redirect('bag:view_bag')


# Checkout-related views
@require_POST
def create_checkout_session(request):
    """View to create a Stripe checkout session."""
    try:
        bag = get_bag(request)
        if not bag:
            return JsonResponse({'error': 'Bag is empty.'}, status=400)

        total, delivery, grand_total = calculate_totals(bag)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': settings.STRIPE_CURRENCY,
                    'product_data': {'name': 'Total Order'},
                    'unit_amount': int(grand_total * 100),
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


def checkout(request):
    """View to handle the checkout process."""
    bag = get_bag(request)
    if not bag:
        messages.error(
            request,
            "Your bag is empty. Add items before proceeding to checkout."
        )
        return redirect('bag:view_bag')

    total, delivery, grand_total = calculate_totals(bag)
    form = OrderForm()

    try:
        # Create Stripe PaymentIntent
        intent = stripe.PaymentIntent.create(
            amount=int(grand_total * 100),
            currency=settings.STRIPE_CURRENCY,
            metadata={'bag': str(bag)}
        )
        context = {
            'form': form,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'client_secret': intent.client_secret,
            'total': number_format(total, decimal_pos=2, use_l10n=True),
            'delivery': number_format(delivery, decimal_pos=2, use_l10n=True),
            'grand_total': number_format
            (grand_total, decimal_pos=2, use_l10n=True),
        }
        return render(request, 'checkout/checkout.html', context)
    except Exception as e:
        messages.error(
            request,
            "An error occurred while processing your payment.Please try again."
        )
        return redirect('bag:view_bag')
