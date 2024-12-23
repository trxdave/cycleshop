"""
URL configuration for cycleshop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import subscribe_newsletter
from django.views.generic import TemplateView
from cycleshop.sitemaps import StaticViewSitemap

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('products/', include('products.urls')),
    path('accounts/', include('allauth.urls')),
    path('bag/', include('bag.urls', namespace='bag')),
    path('search/', views.search_request, name='search_results'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path(
        'subscribe',
        subscribe_newsletter,
        name='subscribe_newsletter'
    ),
    path(
        'checkout/',
        include('checkout.urls', namespace='checkout')
    ),
    path(
        'sitemap.xml',
        TemplateView.as_view(
            template_name="sitemap.xml",
            content_type="application/xml"
        ),
        name='sitemap'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
