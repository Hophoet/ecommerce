from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from .models import Item, OrderItem
# Create your tests here.
#user model
User = get_user_model()
#home page test TestCase
class HomeTestCase(TestCase):
    """ home test case """
    def setUp(self):
        """ setup of the home test case """
        pass

    def test_home_page_return_200(self):
        """ home page return 200 status case test case """
        #get request to the home page
        response = self.client.get(reverse('core:home'))
        #testing
        self.assertEqual(response.status_code, 200)

#post detail
class ItemDetailTestCase(TestCase):
    """ item detail test case """
    def setUp(self):
        """ post detail test case setup """
        #user creation
        self.client.post(reverse('account_signup'),
        {
            'username':'test',
            'email':'test@gmail.com',
            'password1':'TestPassword00',
            'password2':'TestPassword00'
        })
        #get of the user
        self.user = User.objects.get(username='test', email='test@gmail.com')
        #creation of a item
        Item.objects.create(title='test item', price=30.5, category=('S','Shirt'),
        label=('P','primary'), slug='testItemSlug', description='test item description')
        #get of the item
        self.item = Item.objects.get(title='test item')

    def test_item_detail_page_return_200(self):
        """ item detail page return 200 status code test case """

        #get of the item slug
        item_slug = self.item.slug
        #request
        response = self.client.get(reverse('core:product',
            kwargs={
                'slug':item_slug
            }
        ))
        #test
        self.assertEqual(response.status_code, 200)

    def test_item_add_to_cart(self):
        """ item add to cart """
        #order item count
        order_items_count = OrderItem.objects.count()
        #request to add item to card
        response = self.client.get(reverse('core:add-to-cart', kwargs={
            'slug':self.item.slug
        }))
        #order item count after the request
        new_order_items_count = OrderItem.objects.count()
        #test
        self.assertEqual(new_order_items_count, order_items_count+1)

    def test_item_remove_from_cart(self):
        """ item remove from cart """
        #add item to the cart
        self.client.get(reverse('core:add-to-cart', kwargs={
            'slug':self.item.slug
        }))
        #order item count
        order_items_count = OrderItem.objects.count()
        #remove the item
        self.client.get(reverse('core:remove-from-cart', kwargs={
            'slug':self.item.slug
        }))
        #order item count after the remove
        new_order_items_count = OrderItem.objects.count()
        #test
        self.assertEqual(order_items_count, new_order_items_count + 1)
