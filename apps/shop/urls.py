from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('shop/', views.shop, name='shop'),
    path('product/<int:product_id>/', views.product, name='product'),
    path('categories/', views.categories, name='categories'),
    path('cart/', views.cart, name='cart'),
    path('cart/delivered/', views.mark_delivered, name='mark_delivered'),
    path('checkout/', views.checkout, name='checkout'),
    path('contact/', views.contact, name='contact'),   
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/<int:item_id>/decrease/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/<int:item_id>/increase/', views.increase_quantity, name='increase_quantity'),
    path('api/orders', views.create_order, name='create_order'),
    path('api/orders/<str:order_id>/capture', views.capture_order, name='capture_order'),
    path('orders/<str:cart_id>/', views.order, name='order'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('remove-coupon/', views.remove_coupon, name='remove_coupon'),
]
