from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'email', 'phone_number', 'total', 'date')
    search_fields = ('id', 'full_name', 'email')
    list_filter = ('date',)
    readonly_fields = ('date',)

    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'full_name', 'email', 'phone_number', 'total')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'postal_code', 'country')
        }),
        ('Additional Info', {
            'fields': ('date',)
        }),
    )
