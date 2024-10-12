
from pyexpat.errors import messages
from django.contrib.auth import authenticate, login , logout
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile, LoginHistory
from django.contrib.auth.models import User
from social.models import Friend, Post , FriendRequest
from .models import Profile

def user_account(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
        user_posts = Post.objects.filter(user=user).order_by('-created_at')
        post_count = user_posts.count()
    except UserProfile.DoesNotExist:
        user_profile = None
        user_posts = None
        
    friend_count = Friend.objects.filter(user=user).count()
    friend_request_count = FriendRequest.objects.filter(to_user=user).count()
        
    return render(request, 'user_account.html', {
        'user_profile': user_profile, 
        'user_posts': user_posts,
        'post_count': post_count, 
        'friend_request_count': friend_request_count,
        'friend_count': friend_count, 
    })
    


@login_required
def user_settings(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None

    if request.method == 'POST':
        if 'passwordChangeForm' in request.POST:
            current_password = request.POST.get('currentPassword')
            new_password = request.POST.get('newPassword')
            confirm_new_password = request.POST.get('confirmNewPassword')

            user = authenticate(request, username=request.user.username, password=current_password)
            if user is not None:
                if new_password == confirm_new_password:
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Your password has been changed successfully !')
                    login(request, user)  # Re-authenticate user to update session
                    return redirect('user_settings')
                else:
                    messages.error(request, 'New passwords do not match.')
            else:
                messages.error(request, 'Invalid current password.')

        elif 'privacySettingsForm_name' in request.POST:
            visibility = request.POST.get('accountVisibility')
            if user_profile:
                user_profile.account_visibility = visibility
                user_profile.save()
            else:
                UserProfile.objects.create(user=user, account_visibility=visibility)
        
        elif 'profilechnagesForm' in request.POST:
            # Update user's first name and last name
            request.user.first_name = request.POST.get('firstName', '')
            request.user.last_name = request.POST.get('lastName', '')
            request.user.save()
    
            # Update user's profile description
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.description = request.POST.get('description', '')
            profile.save()

            profile_picture = request.FILES.get('profilePicture')
            if profile_picture:
                if user_profile:
                    user_profile.profile_picture = profile_picture
                    user_profile.save()
                else:
                    UserProfile.objects.create(user=user, profile_picture=profile_picture)

            return redirect('user_settings')
    
    # get login data from DB    
    login_history = LoginHistory.objects.filter(user=user).order_by('-last_login')
    return render(request, 'user_settings.html', {'user': user, 'user_profile': user_profile, 'login_history': login_history})



def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        logout(request)
        return redirect('user_login')

def delete_data(request):
    if request.method == 'POST':
        user = request.user
        UserProfile.objects.filter(user=user).delete()
        LoginHistory.objects.filter(user=user).delete()
        return redirect('user_settings')
    
    