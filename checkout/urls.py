from django.urls import path
from . import views
from django.shortcuts import render
from .webhooks import stripe_webhook

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout_view, name='checkout'),

    #Payment
    path('process/', views.process_payment, name='process_payment'),
    path('checkout_success/', views.checkout_success, name='checkout_success'),
    path('checkout_failure/', views.checkout_failure, name='checkout_failure'),

    # Order
    path('order-history/', views.order_history, name='order_history'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    # Webhooks
    path('wh/', stripe_webhook, name='webhook'),
    path('cache_checkout_data/', views.cache_checkout_data, name='cache_checkout_data'),
]