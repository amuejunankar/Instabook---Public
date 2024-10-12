# models.py

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    account_visibility = models.CharField(max_length=10, choices=[('public', 'Public'), ('private', 'Private')], default='public')

    def __str__(self):
        return self.user.username
    
    class Meta:
        app_label = 'user_account'

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_login = models.DateTimeField()
    ip_address = models.CharField(max_length=45, default='Unknown')

    def __str__(self):
        return f"{self.user.username} - {self.last_login}"
    
    class Meta:
        app_label = 'user_account'
        
        

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
