from django.urls import path
from . import views
from checkout import views as checkout_views

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout_view, name='checkout'),
    path('process/', views.process_payment, name='process_payment'),

    # Order
     path('order-history/', checkout_views.order_history, name='order_history'),
]