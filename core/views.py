from django.shortcuts import render, redirect, get_object_or_404
from  django.views.generic import ListView, DetailView
from django.utils import timezone
from .models import Item, OrderItem, Order
# Create your views here.
class HomeView(ListView):
    model = Item
    template_name = 'home.html'

class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'



def checkout(request):
    context = {}
    return render(request, 'checkout.html', context)


def add_to_cart(request, slug):
    """ add to cart view method manager """
    #get of the item
    item = get_object_or_404(Item, slug=slug)
    #geting of the order_item, or creation if not exists
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    #get of the order of the current user, and (not ordered)
    order_queryset = Order.objects.filter(user=request.user, ordered=False)
    #case: if the user has alrady an unordered order
    if order_queryset.exists():
        #get of the order in the query set
        order = order_queryset[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            #grow the quantity by 1 whit
            order_item.quantity += 1
            order_item.save()
        #the item not in the cart
        else:
            #add in the cart
            order.items.add(order_item)
    else:
        #the user has not alrady an unordered order
        ordered_date = timezone.now()
        #creation of a new order
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date
        )
        #adding the current item to add in the cart
        order.items.add(order_item)


    return redirect('core:product', slug=slug)
