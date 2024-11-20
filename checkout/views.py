import stripe
import json
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from checkout.models import Order
from products.models import Product
from .forms import OrderForm
import logging

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

# Helper Function: Calculate Total
def calculate_total(request):
    bag = request.session.get('bag', {})
    total = 0
    for item_id, item_data in bag.items():
        product = get_object_or_404(Product, id=item_id)
        total += product.price * item_data['quantity']
    return total

# Helper Function: Send Confirmation Email
def send_confirmation_email(order, user_email):
    try:
        subject = 'Your Order Confirmation - CycleShop'
        message = render_to_string('checkout/order_confirmation_email.html', {
            'order': order,
        })
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
    except Exception as e:
        # Handle or log email errors
        pass

# Checkout View
def checkout_view(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.total = calculate_total(request)
            order.status = "pending"
            order.save()

            # Create Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),
                currency=settings.STRIPE_CURRENCY,
                metadata={'order_id': order.id}
            )
            print(f"Stripe PaymentIntent Metadata: {intent.metadata}")

            # Pass data to the template
            context = {
                'form': form,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                'client_secret': intent.client_secret,
                'order_id': order.id,
            }
            return render(request, 'checkout/checkout.html', context)
    else:
        form = OrderForm()

    # For GET requests
    context = {
        'form': form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': None,
    }
    return render(request, 'checkout/checkout.html', context)

# Checkout Success View
@login_required
def checkout_success(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status != "completed":
            order.status = "completed"
            order.save()

        # Send confirmation email
        send_confirmation_email(order, request.user.email)

        # Clear the shopping bag
        request.session['bag'] = {}
        request.session['bag_items_count'] = 0

        messages.success(request, "Thank you! Your order was successful and a confirmation email has been sent.")
        return render(request, 'checkout/checkout_success.html', {'order': order})
    except Exception:
        messages.error(request, "No matching order found.")
        return redirect('checkout:checkout')

# Checkout Failure View
def checkout_failure(request):
    messages.error(request, "Your payment failed. Please try again or contact support.")
    return render(request, 'checkout/checkout_failure.html')

# Order History View
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user, status="completed").order_by('-date')
    return render(request, 'checkout/order_history.html', {'orders': orders})

# Order Detail View
@login_required
@login_required
def order_detail(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        logger.info(f"Order retrieved: {order}")
        return render(request, 'checkout/order_detail.html', {'order': order})
    except Exception as e:
        logger.error(f"Error retrieving order: {e}")
        messages.error(request, "Order not found.")
        return redirect('checkout:order_history')

# Cache Checkout Data
@require_POST
@csrf_exempt
def cache_checkout_data(request):
    try:
        data = json.loads(request.body)

        # Create and save the order
        order_id = create_order(request)
        print(f"Order ID created and sent: {order_id}")

        # Return the order_id to the frontend
        return JsonResponse({'status': 'success', 'order_id': order_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

# Create Order Function
def create_order(request):
    try:
        data = json.loads(request.body)
        order = Order(
            user=request.user if request.user.is_authenticated else None,
            full_name=data.get('full_name', 'Guest User'),
            email=data.get('email', ''),
            phone_number=data.get('phone_number', ''),
            address=data.get('address', ''),
            city=data.get('city', ''),
            postal_code=data.get('postal_code', ''),
            country=data.get('country', ''),
            total=calculate_total(request),
            status="pending",
        )
        order.save()
        return order.id
    except Exception as e:
        raise ValueError(f"Failed to create order: {str(e)}")

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Fulfill the purchase or update order status
    elif event['type'] == 'payment_intent.payment_failed':
        # Handle the failure
        pass

    return HttpResponse(status=200)
