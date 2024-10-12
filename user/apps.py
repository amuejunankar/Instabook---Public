from django.apps import AppConfig
# from django.contrib.auth.signals import user_logged_in
# from .signals import record_login_history  # Import the signal handler function

class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'

    # def ready(self):
    #     # Connect the record_login_history function to the user_logged_in signal
    #     user_logged_in.connect(record_login_history)
