# Generated by Django 5.1.2 on 2024-10-19 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(help_text='Upload 300x300 image', null=True, upload_to='products/'),
        ),
    ]
