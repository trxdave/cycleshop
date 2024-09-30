from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('category/<str:category>/', views.product_category, name='product_category'),
    path('road-bikes/', views.road_bikes, name='road_bikes'),
    path('mountain-bikes/', views.mountain_bikes, name='mountain_bikes'),
    path('electric-bikes/', views.electric_bikes, name='electric_bikes'),
    path('kids-bikes/', views.kids_bikes, name='kids_bikes'),
    path('clothing/', views.clothing, name='clothing'),
    path('accessories/', views.accessories, name='accessories'),
    path('return-exchange/', views.return_exchange, name='return_exchange'),
    path('faq/', views.faq, name='faq'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)