from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply value by arg."""
    try:
        return float(value) * float(arg)
    except (TypeError, ValueError):
        return ''