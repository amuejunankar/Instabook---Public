from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.user_signup, name='user_signup'),
    path('login/', views.user_login, name='user_login'),
    path('signupOTP/', views.signupOTP, name='signupOTP'),
    
]

urlpatterns += [
    path("forgot_password", views.forgot_password, name="forgot_password"),
    path("otp_verification", views.otp_verification, name="otp_verification"),
    path("reset_password", views.reset_password, name="reset_password"),

]

