from django.urls import path
from . import views

app_name = 'bag'

urlpatterns = [
    path('', views.view_bag, name='view_bag'),
    path('add_to_bag/<int:product_id>/', views.add_to_bag, name='add_to_bag'),
    path('remove/<int:product_id>/', views.remove_from_bag, name='remove_from_bag'),
    path('update_quantity/<int:product_id>/', views.update_quantity, name='update_quantity'),
    path('checkout/', views.checkout, name='checkout'),]