
# # signals.py

# from django.utils import timezone
# from user_account.models import LoginHistory  # Import LoginHistory here

# def record_login_history(sender, request, user, **kwargs):
#     if user is not None and user.is_authenticated:
#         current_time = timezone.now()
#         ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
#         LoginHistory.objects.create(user=user, last_login=current_time, ip_address=ip_address)
