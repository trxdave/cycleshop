import stripe
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from checkout.models import Order
from .forms import OrderForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from products.models import Product

stripe.api_key = settings.STRIPE_SECRET_KEY

# View to handle checkout process and order creation
def checkout_view(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.total = calculate_total(request)
            order.status = "completed"
            order.save()

            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),
                currency=settings.STRIPE_CURRENCY,
                metadata={'order_id': order.id}
            )

            context = {
                'form': form,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                'client_secret': intent.client_secret,
                'order_id': order.id,
            }
            return render(request, 'checkout/checkout.html', context)
    else:
        form = OrderForm()

    context = {
        'form': form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': None,
    }
    return render(request, 'checkout/checkout.html', context)

# View to create a PaymentIntent (for AJAX or API-based processing)
def create_payment_intent(request):
    try:
        intent = stripe.PaymentIntent.create(
            amount=calculate_total(request) * 100,  # Convert to cents
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
    """ View to handle successful checkouts, send a confirmation email, and clear the cart. """
    # Retrieve the order using the order_id from the URL
    order = get_object_or_404(Order, id=order_id)
    user_email = request.user.email

    subject = 'Your Order Confirmation - CycleShop'
    message = render_to_string('checkout/order_confirmation_email.html', {
        'order': order,
        'user': request.user,
    })

    try:
        # Send confirmation email
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

    storage = messages.get_messages(request)
    storage.used = True

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
@csrf_exempt  # CSRF token may need to be managed differently if used with AJAX
def cache_checkout_data(request):
    try:
        data = json.loads(request.body)
        
        # Validate client_secret and save_info data
        client_secret = data.get('client_secret')
        save_info = data.get('save_info')
        if not client_secret:
            return JsonResponse({'status': 'error', 'message': 'Client secret is missing'}, status=400)

        # Store data in session or any other required processing
        request.session['checkout_data'] = {
            'client_secret': client_secret,
            'save_info': save_info,
        }

        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)