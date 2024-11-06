from django.urls import path
from . import views

urlpatterns = [
    path('', views.checkout_view, name='checkout'),
    path('process/', views.process_payment, name='process_payment'),
]