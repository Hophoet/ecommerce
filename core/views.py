from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from  django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .models import (Item, OrderItem, Order, BillingAddress)
from .forms import CheckoutForm


# Create your views here.
class HomeView(ListView):
    """ Home page view """
    model = Item
    template_name = 'home.html'
    paginate_by = 4
    ordering = 'title'


class ItemDetailView(DetailView):
    """ Item detail page view """
    model = Item
    template_name = 'product.html'

#order summary
class OrderSummaryView(LoginRequiredMixin, View):
    """ Order summary page view """
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an Order")
            return redirect('/')
        context = {'order':order}
        return render(self.request, 'order_summary.html', context)


#payment view
class PaymentView(LoginRequiredMixin, View):
    """ payment page view """
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an Order")
            return redirect('/')
        context = {'order':order}
        return render(self.request, 'payment.html', context)


class CheckoutView(LoginRequiredMixin, View):
    """ Checkout page view """
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an Order")
            return redirect('/')
        form = CheckoutForm()
        context = {
            'form':form,
            'order':order
        }
        return render(self.request, 'checkout.html', context)
    def post(self, *args, **kwargs):
        #if and order exists
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm(self.request.POST or None)
            #check of the validation of the form
            if form.is_valid():
                #get of the user billing info
                user = self.request.user
                street_address = form.cleaned_data['street_address']
                apartment_address = form.cleaned_data['apartment_address']
                contry = form.cleaned_data['contry']
                zip = form.cleaned_data['zip']
                # same_billing_address = form.cleaned_data['same_billing_address']
                # save_info = form.cleaned_data['save_info']
                payment_option = form.cleaned_data['payment_option']
                #saving
                billing_address = BillingAddress.objects.create(user=user, zip=zip,
                street_address=street_address, contry=contry)
                #add the billing address in the order
                order.billing_address = billing_address
                order.save()
                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')


            return redirect('core:checkout')
        #else order not exists
        except ObjectDoesNotExist:
            messages.error(self.request, "You don't have an Order")
            return redirect('core:checkout')



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
            #don't do nothing
            messages.info(request, f'This item is alraidy add.')
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
    """ Remove item view """
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




@login_required
def remove_single_item_from_cart(request, slug):
    """ Remove single item view """
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
            #check if the order_item quantity is greater or equal to 1
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, 'This item was update form your cart.')
            #remove the order item
            else:
                #remove the order item in the order
                order.items.remove(order_item)
                #delete the order item
                order_item.delete()
                #delete the order if is empty
                if not order.items.count():
                    print('Order items count', order.items.count())
                    # order.delete()
        #if the item is not in the cart
        else:
            messages.info(request, 'This item is not in your cart.')
            return redirect('core:order-summary')
    else:
        messages.info(request, 'You do not have an order.')
    return redirect('core:order-summary')



@login_required
def add_single_item_to_cart(request, slug):
    """ add single item to cart view """
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
            #increase by 1 the quantity
            order_item.quantity += 1
            order_item.save()
            messages.info(request, f'This item quantity was updated.')
        #the item not in the cart
        else:
            messages.info(request, f'This item was added to your cart.')
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
        messages.info(request, f'This item was added to your cart.')

    return redirect('core:order-summary')
