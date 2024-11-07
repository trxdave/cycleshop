import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Order
from .forms import OrderForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

stripe.api_key = settings.STRIPE_SECRET_KEY


def checkout_view(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.save()

            # Create a Stripe PaymentIntent
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),
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
    """ The payment and redirect to the appropriate page based on success or failure. """
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
    
    messages.success(request, "Your payment was successful! Thank you for your order.")
    return render(request, 'checkout/checkout_success.html')


def checkout_failure(request):
    messages.error(request, "Your payment failed. Please try again or contact support.")
    return render(request, 'checkout/checkout_failure.html')


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-date')
    context = {'orders': orders}
    return render(request, 'checkout/order_history.html', context)