import stripe
import json
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


# Helper: Calculate Total
def calculate_total(request):
    bag = request.session.get('bag', {})
    total = 0
    for item_id, item_data in bag.items():
        product = get_object_or_404(Product, id=item_id)
        total += product.price * item_data['quantity']
    return total


# Send Confirmation Email
def send_confirmation_email(order, user_email):
    if order.email_sent:
        logger.info(f"Email already sent for Order {order.id}")
        return

    try:
        subject = 'Your Order Confirmation - CycleShop'
        text_content = (
            f"Thank you for your order, {order.full_name}!\n"
            f"Your order ID is {order.id}."
        )
        html_content = render_to_string(
            'checkout/order_confirmation_email.html', {'order': order}
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        order.email_sent = True
        order.save(update_fields=['email_sent'])
        logger.info(f"Order confirmation email sent to {user_email}.")
    except Exception as e:
        logger.error(f"Failed to send order confirmation email: {e}")


# Checkout View
def checkout_view(request):
    form = OrderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            order = form.save(commit=False)
            order.user = (
                request.user if request.user.is_authenticated else None
            )
            order.total = calculate_total(request)
            order.status = "pending"
            order.save()

            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),
                currency=settings.STRIPE_CURRENCY,
                metadata={'order_id': order.id},
            )
            logger.info(f"PaymentIntent created for order ID {order.id}")

            context = {
                'form': form,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                'client_secret': intent.client_secret,
                'order_id': order.id,
            }
            return render(request, 'checkout/checkout.html', context)
        except Exception as e:
            logger.error(f"Error during checkout: {e}")
            messages.error(
                request, "An error occurred during checkout. Please try again."
            )
            return redirect('checkout:checkout')

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

        # Clear the shopping bag
        request.session['bag'] = {}
        request.session['bag_items_count'] = 0

        messages.success(request, "Thank you! Your order was successful.")
        return render(
            request,
            'checkout/checkout_success.html',
            {'order': order},
        )
    except Exception as e:
        logger.error(f"Error in checkout success view: {e}")
        messages.error(
            request, "An error occurred while processing your order."
        )
        return redirect('checkout:checkout')


# Checkout Failure View
def checkout_failure(request):
    messages.error(
        request, "Your payment failed. Please try again or contact support."
    )
    return render(request, 'checkout/checkout_failure.html')


# Order History View
@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user, status="completed"
    ).order_by('-date')
    return render(request, 'checkout/order_history.html', {'orders': orders})


# Order Detail View
@login_required
def order_detail(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        logger.info(f"Order detail retrieved for order ID {order.id}")
        return render(
            request, 'checkout/order_detail.html', {'order': order}
        )
    except Exception as e:
        logger.error(f"Error retrieving order detail: {e}")
        messages.error(request, "Order not found.")
        return redirect('checkout:order_history')


# Cache Checkout Data
@require_POST
@csrf_exempt
def cache_checkout_data(request):
    try:
        data = json.loads(request.body)
        logger.debug(f"Cache checkout data received: {data}")

        order_id = create_order(request)
        logger.info(f"Order ID {order_id} cached successfully.")
        return JsonResponse({'status': 'success', 'order_id': order_id})
    except Exception as e:
        logger.error(f"Error caching checkout data: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# Create Order Function
def create_order(request):
    try:
        data = json.loads(request.body)
        required_fields = [
            'full_name', 'email', 'address', 'city', 'postal_code', 'country'
        ]
        for field in required_fields:
            if not data.get(field):
                raise ValueError(f"Missing required field: {field}")

        order = Order(
            user=request.user if request.user.is_authenticated else None,
            full_name=data['full_name'],
            email=data['email'],
            phone_number=data.get('phone_number', ''),
            address=data['address'],
            city=data['city'],
            postal_code=data['postal_code'],
            country=data['country'],
            total=calculate_total(request),
            status="pending",
        )
        order.save()
        return order.id
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise ValueError(f"Failed to create order: {e}")


# Stripe Webhook
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        logger.info(f"Payment succeeded: {payment_intent['id']}")

        # Extract metadata (order_id, email, etc.)
        metadata = payment_intent.get('metadata', {})
        order_id = metadata.get('order_id')

        # Update order status
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.status = "completed"
                order.save()
                logger.info(f"Order {order_id} marked as completed")
            except Order.DoesNotExist:
                logger.error(f"Order with ID {order_id} does not exist")

    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        logger.warning(f"Payment failed: {payment_intent['id']}")
    else:
        logger.info(f"Unhandled event type: {event['type']}")

    return HttpResponse(status=200)
