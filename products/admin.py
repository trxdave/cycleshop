from django.contrib import admin
from .models import Product, Category

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'available', 'category')
    list_filter = ('available', 'category')
    search_fields = ('name', 'category__name')

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
