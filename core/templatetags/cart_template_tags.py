from django import template
from core.models import Order

register = template.Library()

@register.filter
def cart_item_count(user):
    print('USER', dir(user))
    if user.is_authenticated:
        orderqs = Order.objects.filter(user=user, ordered=False)
        if orderqs.exists():
            return orderqs[0].items.count()
    return 0
