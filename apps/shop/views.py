from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from apps.shop.models import Product, Category, Cart, CartItem
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from apps.shop.forms import ReviewForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
import logging
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from paypalserversdk.http.auth.o_auth_2 import ClientCredentialsAuthCredentials
from paypalserversdk.logging.configuration.api_logging_configuration import (
    LoggingConfiguration,
    RequestLoggingConfiguration,
    ResponseLoggingConfiguration,
)
from paypalserversdk.paypal_serversdk_client import PaypalServersdkClient
from paypalserversdk.controllers.orders_controller import OrdersController
from paypalserversdk.controllers.payments_controller import PaymentsController
from paypalserversdk.models.amount_with_breakdown import AmountWithBreakdown
from paypalserversdk.models.checkout_payment_intent import CheckoutPaymentIntent
from paypalserversdk.models.order_request import OrderRequest
from paypalserversdk.models.purchase_unit_request import PurchaseUnitRequest
from paypalserversdk.api_helper import ApiHelper
from django.db.models import Q, Count
from datetime import timedelta

# Initialize PayPal client
paypal_client = PaypalServersdkClient(
    client_credentials_auth_credentials=ClientCredentialsAuthCredentials(
        o_auth_client_id=settings.PAYPAL_CLIENT_ID,
        o_auth_client_secret=settings.PAYPAL_CLIENT_SECRET,
    ),
    logging_configuration=LoggingConfiguration(
        log_level=logging.INFO,
        mask_sensitive_headers=False,  # Set to True in production
        request_logging_config=RequestLoggingConfiguration(
            log_headers=True, 
            log_body=True
        ),
        response_logging_config=ResponseLoggingConfiguration(
            log_headers=True, 
            log_body=True
        ),
    ),
)

orders_controller = paypal_client.orders
payments_controller = paypal_client.payments

def get_cart(request):
    carts = Cart.objects.filter(user=request.user, status='active')
    return carts.first() if carts else Cart.objects.create(user=request.user, status='active')

def get_recommended_products(request, total_products=4):
    """
    Get recommended products based on multiple factors:
    1. User's purchase history
    2. Current cart items' categories
    3. Popular products in the last 30 days
    4. Products from similar categories
    
    Args:
        request: HttpRequest object
        total_products: Number of products to return (default: 4)
        
    Returns:
        QuerySet of recommended products
    """
    user = request.user
    # Get current cart items
    cart = get_cart(request)
    cart_items = cart.cartitem_set.all()
    cart_product_ids = [item.product.id for item in cart_items]
    
    # Initialize empty QuerySet
    recommended = Product.objects.none()
    
    # 1. Get categories from user's current cart
    cart_categories = set()
    for item in cart_items:
        cart_categories.add(item.product.category.id)
    
    # 2. Get user's purchase history (last 90 days)
    past_orders = Cart.objects.filter(
        user=user,
        created_at__gte=timezone.now() - timedelta(days=90),
        status='completed'
    )
    
    purchased_products = []
    purchased_categories = set()
    for order in past_orders:
        for item in order.orderitem_set.all():
            purchased_products.append(item.product.id)
            purchased_categories.add(item.product.category.id)
    
    # Combine current cart and purchase history categories
    relevant_categories = cart_categories.union(purchased_categories)
    
    # 3. Get products from similar categories, excluding cart items
    if relevant_categories:
        category_recommendations = Product.objects.filter(
            category__id__in=relevant_categories,
            is_active=True
        ).exclude(
            id__in=cart_product_ids + purchased_products
        )
        recommended = recommended.union(category_recommendations)
    
    # 4. Get popular products from the last 30 days
    popular_products = CartItem.objects.filter(
        cart__created_at__gte=timezone.now() - timedelta(days=30),
        cart__status='completed'
    ).values('product').annotate(
        count=Count('product')
    ).order_by('-count')
    
    popular_product_ids = [item['product'] for item in popular_products]
    popular_recommendations = Product.objects.filter(
        id__in=popular_product_ids,
    ).exclude(
        id__in=cart_product_ids + purchased_products
    )
    
    # Combine recommendations
    recommended = recommended.union(popular_recommendations)
    
    # If we still don't have enough recommendations, add random active products
    if recommended.count() < total_products:
        random_products = Product.objects.exclude(
            id__in=cart_product_ids + purchased_products + list(recommended.values_list('id', flat=True))
        )
        recommended = recommended.union(random_products)
    
    # Return the specified number of products
    return recommended[:total_products]


products = [
    {'name': 'Smartphone X', 'price': 699.99, 'image': 'https://via.placeholder.com/300x300?text=Smartphone+X'},
    {'name': 'Laptop Pro', 'price': 1299.99, 'image': 'https://via.placeholder.com/300x300?text=Laptop+Pro'},
    {'name': 'Wireless Earbuds', 'price': 129.99, 'image': 'https://via.placeholder.com/300x300?text=Wireless+Earbuds'},
    {'name': 'Smart Watch', 'price': 249.99, 'image': 'https://via.placeholder.com/300x300?text=Smart+Watch'},
    {'name': '4K TV', 'price': 799.99, 'image': 'https://via.placeholder.com/300x300?text=4K+TV'},
    {'name': 'Gaming Console', 'price': 499.99, 'image': 'https://via.placeholder.com/300x300?text=Gaming+Console'},
    {'name': 'Digital Camera', 'price': 599.99, 'image': 'https://via.placeholder.com/300x300?text=Digital+Camera'},
    {'name': 'Bluetooth Speaker', 'price': 79.99, 'image': 'https://via.placeholder.com/300x300?text=Bluetooth+Speaker'},
]

categories = [
    {'name': 'Electronics', 'icon': 'fas fa-mobile-alt'},
    {'name': 'Clothing', 'icon': 'fas fa-tshirt'},
    {'name': 'Home & Garden', 'icon': 'fas fa-home'},
    {'name': 'Sports & Outdoors', 'icon': 'fas fa-football-ball'},
    {'name': 'Beauty & Personal Care', 'icon': 'fas fa-spa'},
    {'name': 'Books & Media', 'icon': 'fas fa-book'},
    {'name': 'Toys & Games', 'icon': 'fas fa-gamepad'},
    {'name': 'Automotive', 'icon': 'fas fa-car'},
]

def index(request):

    # Handle newsletter signup
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            messages.success(request, f"Thank you for subscribing with {email}!")

    context = {
        'page': 'Home',
        'featured_products': Product.objects.all()[:4],
        'categories': Category.objects.all()[:4],
    }

    return render(request, 'shop/index.html', context)

def about(request):
    context = {
        'page': 'About Us',
        'company_name': 'ModernShop',
        'founded_year': 2010,
        'mission': 'To provide high-quality products at competitive prices',
        'team_members': [
            {'name': 'John Doe', 'position': 'CEO'},
            {'name': 'Jane Smith', 'position': 'CTO'},
            {'name': 'Mike Johnson', 'position': 'Head of Operations'},
        ],
    }
    return render(request, 'shop/about.html', context)

def shop(request):
    # Annotate products with average rating
    products = Product.objects.all()
    categories = Category.objects.all()

    # Search
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    # Filtering
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    rating = request.GET.get('rating')

    if category:
        products = products.filter(category__name=category)
    if min_price:
        products = products.filter(price__gte=float(min_price))
    if max_price:
        products = products.filter(price__lte=float(max_price))
    # if rating:
    #     products = products.filter(avg_rating__gte=float(rating))

    # Sorting
    sort = request.GET.get('sort', 'latest')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-avg_rating')
    else:  # latest
        products = products.order_by('-created_at')

    # Pagination
    paginator = Paginator(products, 8)  # Show 8 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page': 'Shop',
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category,
        'current_sort': sort,
        'current_min_price': min_price,
        'current_max_price': max_price,
        'current_rating': rating,
        'search_query': search_query,  # Add this line
    }
    return render(request, 'shop/shop.html', context)


def categories(request):
    return render(request, 'shop/categories.html', {
        'page': 'Categories',
        'categories': Category.objects.all(),
    })

def product(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Pagination
    paginator = Paginator(reviews, 3)  # Show 5 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user  # Assuming the user is logged in
            review.save()
            messages.success(request, 'Your review has been submitted.')
    else:
        form = ReviewForm()

    context = {
        'product': product,
        'reviews': page_obj,  # Use page_obj instead of reviews
        'avg_rating': avg_rating,
        'form': form,
    }
    return render(request, 'shop/product.html', context)

def checkout(request):
    # Sample order summary
    order_items = [
        {'name': 'Smartphone X', 'price': 699.99, 'quantity': 1},
        {'name': 'Wireless Earbuds', 'price': 129.99, 'quantity': 2},
    ]
    subtotal = sum(item['price'] * item['quantity'] for item in order_items)
    tax = subtotal * 0.1  # Assuming 10% tax
    shipping = 10.00
    total = subtotal + tax + shipping
    context = {
        'page': 'Checkout',
        'order_items': order_items,
        'subtotal': subtotal,
        'tax': tax,
        'shipping': shipping,
        'total': total,
    }
    return render(request, 'shop/checkout.html', context)

def contact(request):
    context = {
        'page': 'Contact Us',
        'company_name': 'ModernShop',
        'address': '123 Shop Street, City, Country',
        'phone': '+1 (555) 123-4567',
        'email': 'info@modernshop.com',
    }
    return render(request, 'shop/contact.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    # Get or create cart for user
    cart = get_cart(request)

    # Check if product already in cart
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    # If item already existed, update quantity
    if not item_created:
        cart_item.quantity += quantity
        cart_item.save()

    # Check if requested quantity is available in stock
    if product.stock < cart_item.quantity:
        messages.error(request, "Sorry, we don't have enough stock for this item.")
        cart_item.quantity = product.stock
        cart_item.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_data = {
            'total_items': cart.get_total_items(),
            'total_price': cart.get_total(),
            'item_count': cart_item.quantity,
        }
        return JsonResponse(cart_data)

    messages.success(request, f"{product.name} added to your cart.")
    return redirect('shop:cart')

@login_required
def cart(request):
    cart = get_cart(request)
    cart_items = cart.cartitem_set.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'recommended_products': get_recommended_products(request, 4),
    }
    return render(request, 'shop/cart.html', context)

@login_required
def update_cart(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 0))
        
        if quantity > 0:
            if quantity > cart_item.product.stock:
                messages.error(request, "Sorry, we don't have enough stock for this item.")
                quantity = cart_item.product.stock
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = cart_item.cart
            cart_data = {
                'total_items': cart.get_total_items(),
                'total_price': cart.get_total(),
                'item_total': cart_item.get_total(),
            }
            return JsonResponse(cart_data)

    return redirect('shop:cart')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('shop:cart')

@login_required
def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    
    # Recalculate cart totals
    cart_item.cart.update_totals()
    
    messages.success(request, "Cart updated successfully.")
    return redirect('shop:cart')

@login_required
def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    # Optional: Check if we have enough stock
    if hasattr(cart_item.product, 'stock'):
        if cart_item.quantity >= cart_item.product.stock:
            messages.warning(request, f"Sorry, only {cart_item.product.stock} items available in stock.")
            return redirect('shop:cart')
    
    cart_item.quantity += 1
    cart_item.save()
    
    # Recalculate cart totals
    cart_item.cart.update_totals()
    
    messages.success(request, "Cart updated successfully.")
    return redirect('shop:cart')

@login_required
def cart_view(request):
    try:
        cart = get_cart(request)
        cart_items = cart.cartitem_set.all()
    except Cart.DoesNotExist:
        cart = None
        cart_items = []

    # Get related products (example implementation)
    related_products = Product.objects.filter(active=True).exclude(
        id__in=[item.product.id for item in cart_items]
    )[:4] if cart_items else Product.objects.filter(active=True)[:4]

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'related_products': related_products,
    }
    return render(request, 'shop/cart.html', context)

@csrf_exempt
@require_http_methods(["POST"])
def create_order(request):
    """
    Create a PayPal order to start the transaction.
    """
    try:
        # Parse the JSON data from the request body
        data = json.loads(request.body)
        print(f"\nGetting cart from request data...")
        cart = get_cart(request)
        print(f"Cart: {cart}\n")

        # Create the order
        order = orders_controller.orders_create(
            {
                "body": OrderRequest(
                    intent=CheckoutPaymentIntent.CAPTURE,
                    purchase_units=[
                        PurchaseUnitRequest(
                            amount=AmountWithBreakdown(
                                currency_code="USD",
                                value=f"{cart.total}",
                            ),
                        )
                    ],
                )
            }
        )

        # Return the serialized order response
        return JsonResponse(ApiHelper.json_deserialize(
            ApiHelper.json_serialize(order.body)
        ))

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)

@csrf_exempt  # Note: In production, implement proper CSRF protection
@require_http_methods(["POST"])
def capture_order(request, order_id):
    """
    Capture payment for the created order to complete the transaction.
    """
    try:
        order = orders_controller.orders_capture(
            {"id": order_id, "prefer": "return=representation"}
        )
        
        db_order = get_cart(request)
        db_order.status = "paid"
        db_order.save()
        
        # return redirect('users:profile')
        
        # Return the serialized capture response
        return JsonResponse(ApiHelper.json_deserialize(
            ApiHelper.json_serialize(order.body)
        ))

    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)
        

@login_required
def order(request, cart_id):
    # Get the cart object or return 404
    cart = get_object_or_404(Cart, id=cart_id, user=request.user)
    
    # Get all cart items with their related products
    cart_items = cart.cartitem_set.select_related('product').all()
    
    # Calculate tax rate (if you store it in settings or elsewhere)
    tax_rate = 10  # Example: 10%
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'tax_rate': tax_rate,
    }
    
    return render(request, 'shop/order.html', context)
