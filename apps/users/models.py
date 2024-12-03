from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from .managers import MyAccountManager
import hashlib

class Account(AbstractBaseUser):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(verbose_name='email', max_length=80, unique=True)
    gender = models.CharField(choices=GENDER_CHOICES, default='male', max_length=10)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    @property
    def get_avatar(self):
        email = self.email
        email_hash = hashlib.md5(email.encode()).hexdigest()
        root_url = 'https://www.gravatar.com/avatar/'
        avatar = f"{root_url}{email_hash}"
        return avatar
    
    @property
    def get_name(self):
        return self.name if self.name else self.email.split('@')[0]
 

class Address(models.Model):
    user = models.ForeignKey('users.Account', on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.street_address}, {self.city}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other addresses of this user to non-default
            Address.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)

class Subscription(models.Model):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email
    
class Contact(models.Model):
    user = models.ForeignKey('users.Account', on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    email = models.EmailField(verbose_name='email', max_length=60)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} - {self.email}"
