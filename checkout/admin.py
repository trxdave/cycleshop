from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for the Order model."""

    # Fields to display in the admin list view
    list_display = (
        'id', 'user', 'full_name', 'email', 'phone_number',
        'address', 'city', 'postal_code', 'country',
        'date', 'total', 'status',
    )

    # Fields to search in the admin list view
    search_fields = ('id', 'full_name', 'email')

    # Filters for the admin list view
    list_filter = ('status', 'date')

    # Fields to make read-only
    readonly_fields = ('date',)

    # Organize fields into sections
    fieldsets = (
        ('Order Information', {
            'fields': (
                'user', 'full_name', 'email', 'phone_number',
                'total', 'status',
            ),
        }),
        ('Address Information', {
            'fields': (
                'address', 'city', 'postal_code', 'country',
            ),
        }),
        ('Additional Info', {
            'fields': ('date',),
        }),
    )
