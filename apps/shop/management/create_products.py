from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.shop.models import Category, Brand, Product, Review
from django.utils.text import slugify
from faker import Faker
import random
from apps.users.models import Account
from django.db import transaction

class Command(BaseCommand):
    help = 'Deletes all existing records and creates 10 realistic sample products with related data'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Deleting all existing records...'))
        
        # Delete all existing records
        Review.objects.all().delete()
        Product.objects.all().delete()
        Brand.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('All existing records deleted.'))

        fake = Faker()

        # Create categories
        categories = {
            'Electronics': Category.objects.create(name='Electronics'),
            'Clothing': Category.objects.create(name='Clothing'),
            'Books': Category.objects.create(name='Books'),
            'Home & Kitchen': Category.objects.create(name='Home & Kitchen'),
            'Sports & Outdoors': Category.objects.create(name='Sports & Outdoors'),
        }

        # Create brands
        brands = {
            'Electronics': ['Apple', 'Samsung', 'Sony', 'LG', 'Dell'],
            'Clothing': ['Nike', 'Adidas', 'Levi\'s', 'H&M', 'Zara'],
            'Books': ['Penguin', 'HarperCollins', 'Random House', 'Simon & Schuster', 'Hachette'],
            'Home & Kitchen': ['KitchenAid', 'Cuisinart', 'Dyson', 'Philips', 'Bosch'],
            'Sports & Outdoors': ['The North Face', 'Columbia', 'Patagonia', 'Under Armour', 'Coleman'],
        }

        for category, brand_list in brands.items():
            for brand_name in brand_list:
                Brand.objects.create(name=brand_name)

        # Product data
        products = [
            {
                'name': 'iPhone 13 Pro',
                'category': 'Electronics',
                'brand': 'Apple',
                'price': 999.99,
                'description': '6.1-inch Super Retina XDR display with ProMotion. Ceramic Shield front. Textured matte glass back and stainless steel design.'
            },
            {
                'name': 'Samsung 4K Smart TV',
                'category': 'Electronics',
                'brand': 'Samsung',
                'price': 799.99,
                'description': '55-inch 4K Ultra HD Smart LED TV with HDR and Alexa Compatibility.'
            },
            {
                'name': 'Nike Air Zoom Pegasus 38',
                'category': 'Clothing',
                'brand': 'Nike',
                'price': 120.00,
                'description': 'Men\'s running shoes with responsive foam and Zoom Air unit for ultimate comfort.'
            },
            {
                'name': 'Levi\'s 501 Original Fit Jeans',
                'category': 'Clothing',
                'brand': 'Levi\'s',
                'price': 69.50,
                'description': 'The original blue jean since 1873. A cultural icon.'
            },
            {
                'name': 'To Kill a Mockingbird',
                'category': 'Books',
                'brand': 'HarperCollins',
                'price': 14.99,
                'description': 'Harper Lee\'s Pulitzer Prize-winning masterwork of honor and injustice in the deep South.'
            },
            {
                'name': 'The Alchemist',
                'category': 'Books',
                'brand': 'HarperCollins',
                'price': 16.99,
                'description': 'Paulo Coelho\'s masterpiece tells the mystical story of Santiago, an Andalusian shepherd boy who yearns to travel in search of a worldly treasure.'
            },
            {
                'name': 'KitchenAid Stand Mixer',
                'category': 'Home & Kitchen',
                'brand': 'KitchenAid',
                'price': 279.99,
                'description': 'Tilt-Head Stand Mixer with 5-Quart Stainless Steel Bowl and 10 optimized speeds powerful enough for nearly any task or recipe.'
            },
            {
                'name': 'Dyson V11 Vacuum Cleaner',
                'category': 'Home & Kitchen',
                'brand': 'Dyson',
                'price': 599.99,
                'description': 'Cordless stick vacuum with up to 60 minutes of run time and whole-machine filtration for powerful suction.'
            },
            {
                'name': 'The North Face Jacket',
                'category': 'Sports & Outdoors',
                'brand': 'The North Face',
                'price': 149.00,
                'description': 'Men\'s waterproof, breathable GORE-TEX jacket for extreme weather protection.'
            },
            {
                'name': 'Coleman Sundome Tent',
                'category': 'Sports & Outdoors',
                'brand': 'Coleman',
                'price': 79.99,
                'description': '4-Person Dome Tent for camping with Easy Setup & Weathertec System.'
            },
        ]

        # Create products
        for product_data in products:
            product = Product.objects.create(
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                stock=random.randint(10, 100),
                category=categories[product_data['category']],
                brand=Brand.objects.get(name=product_data['brand'])
            )

            # Create 2-5 reviews for each product
            for _ in range(random.randint(2, 5)):
                Review.objects.create(
                    product=product,
                    user=Account.objects.order_by('?').first(),  # Random user
                    rating=random.randint(3, 5),  # More positive bias
                    comment=fake.paragraph(nb_sentences=2)
                )

        self.stdout.write(self.style.SUCCESS('Successfully created 10 realistic sample products with related data'))
