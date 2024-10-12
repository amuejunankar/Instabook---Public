# Models -> ( Posts , Comment, Like )

from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import redirect

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    caption = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Post by {self.user.username}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.id}'


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    liked = models.BooleanField(default=True)
    
    def __str__(self):
        return f'{self.user.username} likes {self.post}'

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('sent', 'Sent'), ('accepted', 'Accepted')], default='sent')

    def __str__(self):
        return f"Friend request from {self.from_user.username} to {self.to_user.username}"

    def accept(self): # this hanfles ur accepting, both side it will show you guys are Friends
        Friend.objects.create(user=self.from_user, friend=self.to_user)
        Friend.objects.create(user=self.to_user, friend=self.from_user)
        self.status = 'accepted'
        self.save()

    def decline(self):
        self.delete()

class Friend(models.Model):
    user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    friend = models.ForeignKey(User, related_name='friend_of', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'friend')
    
    def __str__(self):
        return f"{self.user.username} is friends with {self.friend.username}"
    

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
    )
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_notifications', on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey(Post, related_name='notifications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # Add this field

    def __str__(self):
        return f"{self.sender} {self.notification_type} {self.receiver}"
    


## ------------------ CHATT -----------------------

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatRoom(models.Model):
    users = models.ManyToManyField(User, related_name='chatrooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom created at {self.created_at}"

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False) 