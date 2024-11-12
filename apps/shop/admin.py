from django.contrib import admin
from .models import Category, Brand, Product, Review

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1
    readonly_fields = ('created_at',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'image', 'category', 'brand', 'price', 'stock', 'created_at', 'updated_at')
    list_filter = ('category', 'brand', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'image', 'description', 'price', 'stock')
        }),
        ('Categorization', {
            'fields': ('category', 'brand')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    inlines = [ReviewInline]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user', 'comment')
    readonly_fields = ('created_at',)
