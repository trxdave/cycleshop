import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from checkout.models import Order
from .forms import OrderForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from bag.models import BagItem
from products.models import Product
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout_view(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.total = calculate_total(request)
            order.status = "completed"
            order.save()
            print(f"Order created: {order}, Status: {order.status}")

            print(f"Order created: {order}")

            # Create a Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),  # Total amount in cents
                currency=settings.STRIPE_CURRENCY,
                metadata={'order_id': order.id}
            )

            context = {
                'form': form,
                'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                'client_secret': intent.client_secret,
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

def create_payment_intent(request):
    try:
        intent = stripe.PaymentIntent.create(
            amount=calculate_order_amount(),
            currency='eur',
        )
        return JsonResponse({'client_secret': intent.client_secret})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def process_payment(request):
    """Handle payment and redirect based on success or failure."""
    payment_successful = True

    if payment_successful:
        messages.success(request, "Your payment was successful!")
        return redirect(reverse('checkout_success'))
    else:
        messages.error(request, "There was an error with your payment.")
        return redirect(reverse('checkout_failure'))

def checkout_success(request):
    # Clear the cart session after successful payment
    request.session['bag'] = {}
    request.session['bag_items_count'] = 0

    storage = messages.get_messages(request)
    storage.used = True

    return render(request, 'checkout/checkout_success.html')


def checkout_failure(request):
    messages.error(request, "Your payment failed. Please try again or contact support.")
    return render(request, 'checkout/checkout_failure.html')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user, status="completed").order_by('-date')
    context = {'orders': orders}
    return render(request, 'checkout/order_history.html', context)


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'checkout/order_detail.html', context)


def calculate_total(request):
    bag = request.session.get('bag', {})
    total = 0
    for item_id, item_data in bag.items():
        product = Product.objects.get(id=item_id)
        total += product.price * item_data['quantity']
    return total

@require_POST
@csrf_exempt
def cache_checkout_data(request):
    try:
        # Parse JSON data from the request
        data = json.loads(request.body)
        
        # Retrieve the checkout session ID and other metadata from the data
        session_id = data.get('session_id')
        customer_id = data.get('customer_id')
        client_reference_id = data.get('client_reference_id')

        # Optionally store additional metadata (for example, order info or user info)
        # Example: cache it in the session or a database
        request.session['checkout_data'] = {
            'session_id': session_id,
            'customer_id': customer_id,
            'client_reference_id': client_reference_id,
        }

        # Return a successful response
        return JsonResponse({'status': 'success'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)