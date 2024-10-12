from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    # path('', views.index, name='index'),
    path('user_account/', views.user_account, name='user_account'),
    path('user_settings/', views.user_settings, name='user_settings'),
    path('delete_account/', views.delete_account, name='delete_account'),
    path('delete_data/', views.delete_data, name='delete_data'),
    
]

