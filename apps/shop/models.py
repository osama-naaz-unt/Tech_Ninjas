from django.db import models
from django.db.models import Avg

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', help_text="Resolution of 496x256 px", blank=True, null=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Brand(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='products/', null=True, help_text="Upload 300x300 image")
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
  
    def __str__(self):
        return self.name
    
    @property
    def avg_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('shop:product', args=[str(self.id)])

    def add_to_cart_url(self):
        from django.urls import reverse
        return reverse('shop:add_to_cart', args=[str(self.id)])

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.Account', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
  
    def __str__(self):
        return f"Review for {self.product.name} by {self.user}"

class Cart(models.Model):
    user = models.ForeignKey('users.Account', on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, default='active')
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('shop:order', args=[str(self.id)])

    @property
    def total_items(self):
        return self.cartitem_set.count()

    @property
    def total(self):
        return sum(item.total_price for item in self.cartitem_set.all())

    def get_total_items(self):
        return self.total_items

    def get_total(self):
        return self.total
    
    def update_totals(self):
        total_items = self.cartitem_set.count()
        total_price = sum(item.total_price for item in self.cartitem_set.all())
        
        return {
            'total_items': total_items,
            'total_price': total_price
        }

class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
