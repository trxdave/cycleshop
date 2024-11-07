from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path('', views.checkout_view, name='checkout'),
    path('process/', views.process_payment, name='process_payment'),

    # Order
     path('order-history/', views.order_history, name='order_history'),
     path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]