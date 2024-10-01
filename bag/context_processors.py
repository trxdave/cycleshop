def bag_contents(request):
    bag = request.session.get('bag', {})
    bag_items_count = sum(item['quantity'] for item in bag.values())
    bag_total = sum(item['price'] * item['quanity'] for item in bag.values())

    return {
        'bag_items_count': bag_items_count,
        'bag_total': bag_total,
    }