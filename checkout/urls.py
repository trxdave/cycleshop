from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout_view, name='checkout'),
    path('process/', views.process_payment, name='process_payment'),
    path('success/', views.checkout_success, name='checkout_success'),
    path('failure/', views.checkout_failure, name='checkout_failure'),
]