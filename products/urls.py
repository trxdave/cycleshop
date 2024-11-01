from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<str:category>/',
         views.product_category, name='product_category'),

    # Categories
    path('road-bikes/', views.road_bikes, name='road_bikes'),
    path('mountain-bikes/', views.mountain_bikes, name='mountain_bikes'),
    path('electric-bikes/', views.electric_bikes, name='electric_bikes'),
    path('kids-bikes/', views.kids_bikes, name='kids_bikes'),
    path('clothing/', views.clothing, name='clothing'),
    path('accessories/', views.accessories, name='accessories'),

    # Information pages
    path('return-exchange/', views.return_exchange, name='return_exchange'),
    path('shipping-information/', views.shipping_information,
         name='shipping_information'),
    path('wishlist/', views.view_wishlist, name='wishlist'),
    path('faq/', views.faq, name='faq'),

    # Product Management
    path('manage_products/', views.manage_products, name='manage_products'),
    path('add_products/', views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/',
         views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/',
         views.delete_product, name='delete_product'),

    # Wishlist
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/add/<int:product_id>/',
         views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/',
         views.remove_from_wishlist, name='remove_from_wishlist'),
    path('toggle_wishlist/<int:product_id>/',
         views.toggle_wishlist, name='toggle_wishlist'),

     # Order
     path('order-history/', views.order_history, name='order_history'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
