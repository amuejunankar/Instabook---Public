from django.contrib import admin
from .models import Post, Comment, Like, Friend, FriendRequest

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Friend)
admin.site.register(FriendRequest)


# Chatting purposee

from django.contrib import admin
from .models import ChatRoom, Message, Friend

admin.site.register(ChatRoom)
admin.site.register(Message)

