from decimal import Decimal
from django.conf import settings


def bag_contents(request):
    """
    Context processor to add the shopping bag's contents to the context.
    """
    bag = request.session.get('bag', {})
    bag_total = 0
    bag_items_count = 0

    for item_id, item in bag.items():
        bag_total += item['price'] * item['quantity']
        bag_items_count += item['quantity']

    context = {
        'bag_total': bag_total,
        'bag_items_count': bag_items_count,
    }

    return context