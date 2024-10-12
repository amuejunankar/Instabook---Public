from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from user_account.models import UserProfile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import FriendRequest, Notification, Post, Friend, Comment,Like
from user_account.models import UserProfile
from django.db.models import Q




@login_required
def feeds(request):
    if request.user.is_authenticated:
        friend_requests = FriendRequest.objects.filter(to_user=request.user)
        friends_followed = Friend.objects.filter(user=request.user).values_list('friend', flat=True)
        posts = Post.objects.filter(user__in=friends_followed).order_by('-created_at')
        notification_count = Notification.objects.filter(receiver=request.user, is_read=False).count()

        return render(request, 'feed/feed.html', {
            'friend_request_count': friend_requests.count(),
            'posts': posts,
            'notification_count': notification_count,
        })
    else:
        return redirect('index')



# @login_required
# def feeds(request):
#     # user is authenticated
#     if request.user.is_authenticated:
#         # Fetch friend requests for the current user
#         friend_requests = FriendRequest.objects.filter(to_user=request.user)
        
#         # Fetch friends whom the user follows
#         friends_followed = Friend.objects.filter(user=request.user).values_list('friend', flat=True)
        
#         # Fetch posts from the followed friends
#         posts = Post.objects.filter(user__in=friends_followed).order_by('-created_at')
        
#         return render(request, 'feed/feed.html', {
#             'friend_request_count': friend_requests.count(),
#             'posts': posts
#         })
        
#     else:
#         # user is not authenticated
#         return redirect('index')


# NOT IN USE
# @login_required
# def like_post(request, post_id):
#     post = Post.objects.get(id=post_id)
#     user = request.user
#     try:
#         like = Like.objects.get(user=user, post=post)
#         like.liked = not like.liked
#         like.save()
#     except Like.DoesNotExist:
#         like = Like.objects.create(user=user, post=post, liked=True)
#     return redirect('feed')


@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        if post.likes.filter(user=request.user).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
    return redirect('feed')


@login_required
def create_post(request):
    if request.method == 'POST':
        if 'createPostForm' in request.POST:
            image = request.FILES.get('image')
            caption = request.POST.get('caption')
            if image:
                new_post = Post(user=request.user, image=image, caption=caption)
                new_post.save()
                return redirect('feeds') 
            else:
                print("outside if image")
                return render(request, 'feed/feed.html', {'error_message': 'Please upload an image'})
    else:
        return redirect('feeds')
    


@login_required
def searches(request):
    user = request.user
    if 'SearchUserForm' in request.POST:
        search_item = request.POST.get('searchItem')
        
        users = User.objects.filter(
            (Q(first_name__icontains=search_item) | Q(last_name__icontains=search_item)) & ~Q(id=user.id)
        )
        user_profiles = UserProfile.objects.filter(user__in=users)

        # Get IDs of users to whom the current user has sent friend requests
        friend_requests_sent = FriendRequest.objects.filter(from_user=user).values_list('to_user_id', flat=True)

        # Get IDs of users who are already friends
        friends = Friend.objects.filter(user=user).values_list('friend_id', flat=True)

        return render(request, 'feed/friendSearchList.html', {
            'user_profiles': user_profiles,
            'friend_requests_sent': friend_requests_sent,
            'friends': friends,
            'search_item':search_item
        })
        
    return render(request, 'feed/friendSearchList.html')
    

def send_friend_request(request, user_id):
    from_user = request.user
    to_user = User.objects.get(id=user_id)
    friend_request, created = FriendRequest.objects.get_or_create(from_user=from_user, to_user=to_user)
    if created:
        return redirect('searches')
    else:
        return redirect('searches')
    
    
@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if friend_request.to_user == request.user:
        # friendship already exists
        if not Friend.objects.filter(user=request.user, friend=friend_request.from_user).exists():
            print("1")
            try:
                # make friendship from both sides
                Friend.objects.create(user=request.user, friend=friend_request.from_user)
                Friend.objects.create(user=friend_request.from_user, friend=request.user)
                friend_request.delete()  # felete  request after accepting
            except IntegrityError:
                print("Some Error")
        print("22")
        return redirect('friend_requests')
    else:
        return redirect('feeds')

@login_required
def decline_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)
    if friend_request.to_user == request.user:
        friend_request.delete()
        return redirect('friend_requests')
    else:
        return redirect('feeds')

def cancel_friend_request(request, user_id):
    from_user = request.user
    to_user = User.objects.get(id=user_id)
    friend_request = FriendRequest.objects.filter(from_user=from_user, to_user=to_user).first()
    if friend_request:
        friend_request.delete()
    return redirect('feeds')



@login_required
def friend_requests(request):
    friend_requests = FriendRequest.objects.filter(to_user=request.user)
    return render(request, 'feed/friendrequest.html', {
        'friend_requests': friend_requests, 
        'friend_request_count': friend_requests.count()
    })
    
    
@login_required
def profile_friends_list(request):
    user = request.user
    friends = Friend.objects.filter(user=user)

    # Retrieve profile pictures for each friend
    friend_profiles = {}
    for friend in friends:
        try:
            profile = UserProfile.objects.get(user=friend.friend)
            friend_profiles[friend.friend] = profile.profile_picture
        except UserProfile.DoesNotExist:
            friend_profiles[friend.friend] = None

    return render(request, 'feed/friends.html', {'friends': friends, 'friend_profiles': friend_profiles})

@login_required
def remove_friend(request, friend_id):
    friend_user = get_object_or_404(User, id=friend_id)
    current_user = request.user

    try:
        # Get the Friend object for the current user
        friend_obj_current = Friend.objects.get(user=current_user, friend=friend_user)
        friend_obj_current.delete()

        # Get the Friend object for the friend user
        friend_obj_friend = Friend.objects.get(user=friend_user, friend=current_user)
        friend_obj_friend.delete()

        messages.success(request, f'You have removed {friend_user.username} from your friends list.')
    except Friend.DoesNotExist:
        messages.warning(request, f'You and {friend_user.username} are not friends.')

    return redirect('friends_list')


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        if 'delete' in request.POST:
            post.delete()
            return redirect('user_account')  # Redirect to user account or some other page after deletion
        elif 'like' in request.POST:
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if created:
                # Create a like notification
                Notification.objects.create(
                    sender=request.user,
                    receiver=post.user,
                    notification_type='like',
                    post=post
                )
            else:
                like.delete()
        elif 'comment' in request.POST:
            comment_content = request.POST.get('comment')
            if comment_content:
                Comment.objects.create(user=request.user, post=post, content=comment_content)
                # Create a comment notification
                Notification.objects.create(
                    sender=request.user,
                    receiver=post.user,
                    notification_type='comment',
                    post=post
                )
        elif 'delete_comment' in request.POST:
            comment_id = request.POST.get('comment_id')
            comment = get_object_or_404(Comment, id=comment_id, user=request.user)
            comment.delete()

    return render(request, 'feed/post_detail.html', {'post': post})


# @login_required
# def post_detail(request, post_id):
#     post = get_object_or_404(Post, id=post_id)

#     if request.method == 'POST':
#         if 'delete' in request.POST:
#             post.delete()
#             return redirect('user_account')  # Redirect to user account or some other page after deletion
#         elif 'like' in request.POST:
#             like, created = Like.objects.get_or_create(user=request.user, post=post)
#             if not created:
#                 like.delete()
#         elif 'comment' in request.POST:
#             comment_content = request.POST.get('comment')
#             if comment_content:
#                 Comment.objects.create(user=request.user, post=post, content=comment_content)
#         elif 'delete_comment' in request.POST:
#             comment_id = request.POST.get('comment_id')
#             comment = get_object_or_404(Comment, id=comment_id, user=request.user)
#             comment.delete()

#     return render(request, 'feed/post_detail.html', {'post': post})



def view_profile(request, user_id):
    user_profile = get_object_or_404(UserProfile, user__id=user_id)
    user_posts = Post.objects.filter(user=user_profile.user).order_by('-created_at')
    post_count = user_posts.count()
    friend_count = Friend.objects.filter(user=user_profile.user).count()

    if request.user.is_authenticated:
        friends_of_user = Friend.objects.filter(user=request.user).values_list('friend', flat=True)
        is_friend = user_profile.user.id in friends_of_user or Friend.objects.filter(user=user_profile.user, friend=request.user).exists()
        notification_count = Notification.objects.filter(receiver=request.user, is_read=False).count()
    else:
        is_friend = False
        notification_count = 0

    show_posts = user_profile.account_visibility == 'public' or is_friend

    context = {
        'user_profile': user_profile,
        'user_posts': user_posts,
        'post_count': post_count,
        'friend_count': friend_count,
        'show_posts': show_posts,
        'notification_count': notification_count,
    }
    return render(request, 'feed/profile.html', context)


# latest EDITED

# def view_profile(request, user_id):
#     user_profile = get_object_or_404(UserProfile, user__id=user_id)
#     user_posts = Post.objects.filter(user=user_profile.user).order_by('-created_at')
#     post_count = user_posts.count()
#     friend_count = Friend.objects.filter(user=user_profile.user).count()

#     # Check if the viewing user is authenticated
#     if request.user.is_authenticated:
#         # Get the friends of the logged-in user
#         friends_of_user = Friend.objects.filter(user=request.user).values_list('friend', flat=True)
#         # Check if the profile owner is a friend of the logged-in user
#         is_friend = user_profile.user.id in friends_of_user or Friend.objects.filter(user=user_profile.user, friend=request.user).exists()
#     else:
#         is_friend = False

#     # Determine if the profile should show posts
#     show_posts = user_profile.account_visibility == 'public' or is_friend

#     context = {
#         'user_profile': user_profile,
#         'user_posts': user_posts,
#         'post_count': post_count,
#         'friend_count': friend_count,
#         'show_posts': show_posts,
#     }
#     return render(request, 'feed/profile.html', context)


@login_required
def notifications(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
    return render(request, 'feed/notifications.html', {'notifications': notifications})


@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, receiver=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')



# @login_required
# def friends_list(request):
#     user = request.user
#     friends = Friend.objects.filter(user=user).prefetch_related('friend__userprofile')

#     friend_profiles = {
#         friend.friend.id: friend.friend.userprofile.profile_picture
#         for friend in friends
#     }

#     return render(request, 'feed/friends.html', {'friends': friends, 'friend_profiles': friend_profiles})



## Chatting App


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import ChatRoom, Message, Friend
import logging



@login_required
def get_messages(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    messages = chat_room.messages.order_by('timestamp').values('user__username', 'content', 'timestamp')
    return JsonResponse({'messages': list(messages)})



@login_required
def chat_room(request, room_id):
    chat_room = get_object_or_404(ChatRoom, id=room_id)
    messages = chat_room.messages.order_by('timestamp')
    return render(request, 'feed/chat_room.html', {'chat_room': chat_room, 'messages': messages})


@login_required
def start_chat(request, user_id):
    user_to_chat_with = get_object_or_404(User, id=user_id)
    user = request.user

    # Check if a chat room already exists between the two users
    chat_room = ChatRoom.objects.filter(users=user).filter(users=user_to_chat_with).first()

    # If no chat room exists, create a new one and add the users
    if not chat_room:
        chat_room = ChatRoom.objects.create()
        chat_room.users.add(user, user_to_chat_with)
        chat_room.save()

    return redirect('chat_room', room_id=chat_room.id)



@login_required
def friends_list(request):
    friends = Friend.objects.filter(user=request.user)
    return render(request, 'feed/friends_list.html', {'friends': friends})






@login_required
def send_message(request, room_id):
    if request.method == 'POST':
        try:
            chat_room = get_object_or_404(ChatRoom, id=room_id)
            message_content = request.POST.get('message', '')
            if not message_content:
                return JsonResponse({'error': 'No message content provided'}, status=400)

            message = Message.objects.create(
                chat_room=chat_room,
                user=request.user,
                content=message_content
            )

            return JsonResponse({'message': message.content, 'username': message.user.username, 'timestamp': message.timestamp})
        except Exception as e:
            logging.error(f"Error sending message: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

            
