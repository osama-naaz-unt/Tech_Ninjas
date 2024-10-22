from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from apps.shop.models import Product, Category
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from apps.shop.forms import ReviewForm


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

def cart(request):
    # Sample cart items
    cart_items = [
        {'name': 'Smartphone X', 'price': 699.99, 'quantity': 1},
        {'name': 'Wireless Earbuds', 'price': 129.99, 'quantity': 2},
    ]
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    context = {
        'page': 'Shopping Cart',
        'cart_items': cart_items,
        'total': total,
    }
    return render(request, 'shop/cart.html', context)

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