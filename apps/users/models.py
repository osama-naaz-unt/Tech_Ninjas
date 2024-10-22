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
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
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
 