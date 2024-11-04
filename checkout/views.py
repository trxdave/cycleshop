from django.shortcuts import render, redirect
from .forms import OrderForm
from .models import Order

def checkout_success(request):
    return render(request, 'checkout/success.html')


def checkout_view(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            # Redirect to a success page or initiate payment
            return redirect('checkout_success')
    else:
        form = OrderForm()

    context = {
        'form': form,
    }
    return render(request, 'checkout/checkout.html', context)