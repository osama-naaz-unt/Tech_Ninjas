from django.contrib import admin
from .models import *

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):          
    list_display = ('name', 'email', 'gender', 'created_at',)
    search_fields = ('name', 'email',)
    list_filter = ('gender',)