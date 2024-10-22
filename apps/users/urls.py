from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('reset-password/', views.reset_email, name='reset_email'),
    path('reset-password/success/', views.reset_success, name='reset_success'),
    path('reset-password/new/', views.reset_new, name='reset_new'),
    path('reset-password/done/', views.reset_done, name='reset_done'),
]