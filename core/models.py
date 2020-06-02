from django.db import models
from django.conf import settings
from django.shortcuts import reverse

#Set of the item categories
CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport Wear'),
    ('OW', 'Out Wear'),
)

#Set of the items labels
LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)

class Item(models.Model):
    """ product item model class """
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(null=True, blank=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    quantity = models.IntegerField(default=1)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:product', kwargs={
            'slug':self.slug
        })

    def get_add_to_cart_url(self):
        """ add to cart url getter """
        #redirection to the product detail view page
        return reverse('core:add-to-cart', kwargs={
            'slug':self.slug
        })
    def get_remove_from_cart_url(self):
        """ remove from cart url getter """
        #redirection to the product detail view page
        return reverse('core:remove-from-cart', kwargs={
            'slug':self.slug
        })

class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.quantity} of {self.item.title}'

    #total item price getter
    def get_total_item_price(self):
        """Total item price getter """
        return self.item.price * self.quantity

    #total disount item price getter
    def get_total_discount_item_price(self):
        """Total discount item price getter """
        return self.item.discount_price * self.quantity

    #total saved ammount getter
    def get_amount_saved(self):
        """ Total saved ammount getter """
        return self.get_total_item_price() - self.get_total_discount_item_price()

#Order model
class Order(models.Model):
    """ order actions model class """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username



    #
