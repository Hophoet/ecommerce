
from django.urls import path, include
from . import views

app_name='core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('checkout/', views.checkout, name='checkout'),
    path('product/<slug>/', views.ItemDetailView.as_view(), name='product'),
    path('order-summary/', views.OrderSummaryView.as_view(), name='order-summary'),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/', views.remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('add-single-item-to-cart/<slug>/', views.add_single_item_to_cart, name='add-single-item-to-cart'),


]
