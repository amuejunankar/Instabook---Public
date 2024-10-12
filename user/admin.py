# Register your models here.
from django.contrib import admin
from user_account.models import UserProfile, LoginHistory

admin.site.register(UserProfile)
admin.site.register(LoginHistory)
