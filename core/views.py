from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from  django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .models import Item, OrderItem, Order
# Create your views here.
class HomeView(ListView):
    model = Item
    template_name = 'home.html'
    paginate_by = 2


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'

#order summary
class OrderSummaryView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an Order")
            return redirect('/')
        context = {'order':order}
        return render(self.request, 'order_summary.html', context)

def checkout(request):
    context = {}
    return render(request, 'checkout.html', context)

@login_required
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
            messages.info(request, f'This item quantity({order_item.quantity}) was updated.')
        #the item not in the cart
        else:
            messages.info(request, f'This item({order_item.quantity}) was added to your cart.')
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
        messages.info(request, f'This item({order_item.quantity}) was added to your cart.')

    return redirect('core:product', slug=slug)

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )

    order_queryset = Order.objects.filter(user=request.user, ordered=False)
    #check if the orderqs exists
    if order_queryset.exists():
        order = order_queryset[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, 'This item was removed form your cart.')
        else:
            messages.info(request, 'This item was not in your cart.')
            return redirect('core:product', slug=slug)
    else:
        messages.info(request, 'You do not have an order.')
    return redirect('core:product', slug=slug)
