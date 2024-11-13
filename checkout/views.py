import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from datetime import timedelta
import json
from checkout.models import Order
from products.models import Product
from .forms import OrderForm

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout_view(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Create the order with user info if available
            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.total = calculate_total(request)
            order.status = "pending"
            order.save()

            # Create Stripe PaymentIntent for the total amount
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),  # Stripe requires amount in cents
                currency=settings.STRIPE_CURRENCY,
                metadata={'order_id': order.id}
            )

            # Pass necessary data to the template
            context = {
                'form': form,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                'client_secret': intent.client_secret,
                'order_id': order.id,
            }
            return render(request, 'checkout/checkout.html', context)
    else:
        form = OrderForm()

    # For GET requests, client_secret remains None as no payment is initiated
    context = {
        'form': form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': None,
    }
    return render(request, 'checkout/checkout.html', context)

# View to create a PaymentIntent
def create_payment_intent(request):
    try:
        intent = stripe.PaymentIntent.create(
            amount=calculate_total(request) * 100,
            currency=settings.STRIPE_CURRENCY,
        )
        return JsonResponse({'client_secret': intent.client_secret})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# View to process the payment and redirect based on result
def process_payment(request):
    payment_successful = True

    if payment_successful:
        messages.success(request, "Your payment was successful!")
        return redirect(reverse('checkout_success'))
    else:
        messages.error(request, "There was an error with your payment.")
        return redirect(reverse('checkout_failure'))

# View for successful checkout
def checkout_success(request, order_id):
    """View to handle successful checkouts, send a confirmation email, and clear the cart."""
    # Retrieve the completed order by ID
    order = get_object_or_404(Order, id=order_id, user=request.user, status="completed")

    # Send confirmation email if applicable
    user_email = request.user.email
    subject = 'Your Order Confirmation - CycleShop'
    message = render_to_string('checkout/order_confirmation_email.html', {
        'order': order,
        'user': request.user,
    })

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        messages.success(request, "Thank you! A confirmation email has been sent to your address.")
    except Exception:
        messages.error(request, "Your order was successful, but we couldn't send the confirmation email.")

    # Clear the cart session after successful payment
    request.session['bag'] = {}
    request.session['bag_items_count'] = 0

    return render(request, 'checkout/checkout_success.html', {'order': order})

# View for failed checkout
def checkout_failure(request):
    messages.error(request, "Your payment failed. Please try again or contact support.")
    return render(request, 'checkout/checkout_failure.html')

# View to display user's order history
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user, status="completed").order_by('-date')
    return render(request, 'checkout/order_history.html', {'orders': orders})

# View for order details
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'checkout/order_detail.html', {'order': order})

# Helper function to calculate total cart amount
def calculate_total(request):
    bag = request.session.get('bag', {})
    total = 0
    for item_id, item_data in bag.items():
        product = get_object_or_404(Product, id=item_id)
        total += product.price * item_data['quantity']
    return total

# Endpoint to cache checkout data before final payment confirmation
@require_POST
@csrf_exempt
def cache_checkout_data(request):
    try:
        data = json.loads(request.body)
        request.session['checkout_data'] = {
            'client_secret': data.get('client_secret'),
            'save_info': data.get('save_info'),
        }
        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)