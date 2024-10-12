from django.contrib import admin
from django.urls import include, path
from . import views


urlpatterns = [
    path("", views.feeds, name="feeds"),
    path('create_post/', views.create_post, name='create_post'),
    path('searches/', views.searches, name='searches'),
    
    path('send_friend_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('cancel_friend_request/<int:user_id>/', views.cancel_friend_request, name='cancel_friend_request'),
    
    path('friend-requests/', views.friend_requests, name='friend_requests'),
     path('accept_friend_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline_friend_request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
   
    path('myfriends/', views.profile_friends_list, name='profile_friends_list'),
    path('remove-friend/<int:friend_id>/', views.remove_friend, name='remove_friend'),

    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    
    path('profile/<int:user_id>/', views.view_profile, name='view_profile'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark_as_read/<int:notification_id>/', views.mark_as_read, name='mark_as_read'),

    # OLD Other paths
    # path('chat/room/<int:room_id>/', views.chat_room, name='chat_room'),
    # path('chat/start/<int:user_id>/', views.start_chat, name='start_chat'),
    # path('friends/', views.friends_list, name='friends_list'),
    # path('chat/room/<int:room_id>/send/', views.send_message, name='send_message'),


    # NEW Other URL patterns
    # path('chat/room/<int:room_id>/', views.chat_room, name='chat_room'),
    # path('chat/start/<int:user_id>/', views.start_chat, name='start_chat'),
    # path('friends/', views.friends_list, name='friends_list'),
    # path('feed/chat/room/<int:room_id>/send/', views.send_message, name='send_message'),
    # path('chat/room/<int:room_id>/get_messages/', views.get_messages, name='get_messages'),
    
    path('chat/room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('chat/room/<int:room_id>/get_messages/', views.get_messages, name='get_messages'),
    path('chat/room/<int:room_id>/send_message/', views.send_message, name='send_message'),
    path('friends/', views.friends_list, name='friends_list'),
    path('start_chat/<int:user_id>/', views.start_chat, name='start_chat'),

]


from . import views, consumers

websocket_urlpatterns = [
    path('ws/chat/<int:room_id>/', consumers.ChatConsumer.as_asgi()),
]

