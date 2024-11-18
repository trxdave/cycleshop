import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404, reverse
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
from django.http import Http404

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout_view(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.total = calculate_total(request)
            order.status = "pending"
            order.save()

            # Create Stripe PaymentIntent for the total amount
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),
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
@login_required
def checkout_success(request, order_id):
    try:
        # Fetch the order and ensure it belongs to the current user
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
        # Update the status if not already completed
        if order.status != "completed":
            order.status = "completed"
            order.save()
    except Http404:
        # If the order is not found, redirect to the checkout page with an error message
        messages.error(request, "No matching order found.")
        return redirect('checkout:checkout')

    # Send the confirmation email
    try:
        user_email = request.user.email
        subject = 'Your Order Confirmation - CycleShop'
        message = render_to_string('checkout/order_confirmation_email.html', {
            'order': order,
            'user': request.user,
        })

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )
        messages.success(request, "Thank you! A confirmation email has been sent to your address.")
    except Exception as e:
        # Log or handle email errors
        messages.error(request, "Your order was successful, but we couldn't send the confirmation email.")

    # Clear the user's shopping bag
    request.session['bag'] = {}
    request.session['bag_items_count'] = 0

    # Render the success template with the order details
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

        order_id = create_order(request)

        request.session['checkout_data'] = {
            'client_secret': data.get('client_secret'),
            'save_info': data.get('save_info'),
            'order_id': order_id,
        }
        return JsonResponse({'status': 'success', 'order_id': order_id})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def create_order():
    # Example function to create an order, modify as needed
    order = Order(
        full_name="Test User",
        email="test@example.com",
        phone_number="1234567890",
        address="123 Test St",
        city="Test City",
        postal_code="12345",
        country="Test Country",
        total=100.00,
        status="pending"
    )
    order.save()
    return order.id

def create_order(request):
    try:
        # Parse JSON data from the request body
        data = json.loads(request.body)

        # Extract data to create the order
        order = Order(
            user=request.user if request.user.is_authenticated else None,
            full_name=data.get('full_name', 'Guest User'),
            email=data.get('email', ''),
            phone_number=data.get('phone_number', ''),
            address=data.get('address', ''),
            city=data.get('city', ''),
            postal_code=data.get('postal_code', ''),
            country=data.get('country', ''),
            total=calculate_total(request),  # Ensure this function works
            status="pending",
        )
        order.save()

        return order.id

    except Exception as e:
        raise ValueError(f"Failed to create order: {str(e)}")
