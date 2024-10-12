
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

# @login_required(login_url="../../login")

def index(request):
    return render(request, 'user/index.html')


# --------------------** LOGIN AND SIGNUP **-------------------------
 
from django.contrib.auth import authenticate, login , logout
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User

from user_account.models import LoginHistory
from django.utils import timezone

def user_login(request):
    
    if request.user.is_authenticated:
        return redirect('feeds')
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            # Inside your view function after successful authentication
            current_time = timezone.now()
            ip_address = request.META.get('REMOTE_ADDR', 'Unknown')
            LoginHistory.objects.create(user=user, last_login=current_time, ip_address=ip_address)
            
            return redirect('feeds')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'user/login.html')

def user_logout(request):
    logout(request)
    return redirect('index')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Storeing data in session
        request.session['username'] = username
        request.session['email'] = email
        request.session['password'] = password
        
        # Check username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'user/signup.html', {'error': 'Username is already taken'})
        else:
            otp = generate_otp()
            request.session['session_otp'] = otp  # Store OTP in session
            send_mail("OTP", otp, 'junankgg@gmail.com', [email], fail_silently=True)
            return redirect('signupOTP') 
    else:
        request.session.flush()
        messages = None
        return render(request, 'user/signup.html',{'messages':messages}) 
 
# -----------------------------------< Email > ---------------------

from user_account.models import UserProfile  

def signupOTP(request):
    if request.method == 'POST':
        username = request.session.get('username')
        email = request.session.get('email')
        password = request.session.get('password')
        session_otp = request.session.get('session_otp')
        otp = request.POST['otp']
        
        if otp == session_otp:
            print("OTP MATCHED")
            user = User.objects.create_user(username=username, email=email, password=password)
            user = authenticate(request, username=username, password=password)
            UserProfile.objects.create(user=user)  # Create the UserProfile
            if user:
                request.session.flush()
                login(request, user)
                
                return redirect('index') 
        else:
            request.session.flush() 
            return redirect('user_signup')
        
    return render(request, 'user/signupOTP.html')

# ---------------------------------- RESET PASSWORD -----------------------------------------------------------


def forgot_password(request):
    print("\n'Welcome in FORGOT PASSWORD'")
    # Check if user is already in the process of resetting password
    if request.session.get('password_reset_state') != 'forgot_password':
        # Clear session data to start a new password reset process
        request.session.flush()
        # Set session state to indicate that user is in the forgot password process
        request.session['password_reset_state'] = 'forgot_password'
        
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = generate_otp()
        subject = 'Password Reset OTP'
        html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Reset OTP</title>
                <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap">
                <style>
                    body {{
                        font-family: 'Roboto', sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 500px;
                        margin: 50px auto;
                        padding: 20px;
                        background-color: #ffffff;
                        border-radius: 10px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    }}
                    h1 {{
                        text-align: center;
                        color: #333333;
                        margin-bottom: 20px;
                    }}
                    .otp-container {{
                        background-color: #007bff;
                        color: #ffffff;
                        padding: 20px;
                        border-radius: 5px;
                        text-align: center;
                        margin-bottom: 20px;
                    }}
                    .otp-container p {{
                        margin: 0;
                        font-size: 18px;
                    }}
                    .info {{
                        background-color: #f0f0f0;
                        padding: 15px;
                        border-radius: 5px;
                        margin-bottom: 20px;
                    }}
                    .info p {{
                        margin: 0;
                        font-size: 14px;
                        color: #555555;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Password Reset OTP</h1>
                    <div class="otp-container">
                        <p>Your One Time Password (OTP) for password reset is: <strong>{otp}</strong></p>
                    </div>
                    <div class="info">
                        <p>Important: This OTP is valid for a single use only. Please do not share it with anyone.</p>
                    </div>
                </div>
            </body>
            </html>
        """
        to_emails = [email]

        send_mail(subject, '', settings.EMAIL_HOST_USER, to_emails, html_message=html_content)

        # Store email and OTP in session for verification
        request.session['reset_email'] = email
        request.session['reset_otp'] = otp
        
        return redirect('otp_verification')
        
    # where user enter their email and otp will be sent to his email
    return render(request, 'user/password/forgot_password.html')

def otp_verification(request):
    print("Welcome in OTP VERIFY")
    
    if request.session.get('password_reset_state') == 'forgot_password':
       
        if request.method == 'POST':
            reset_otp = request.session.get('reset_otp')
            otp = request.POST.get('otp')

            if otp == reset_otp:
                # Set session state to indicate that user is in the OTP verification process
                request.session['password_reset_state'] = 'otp_verification'
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                return redirect('forgot_password')
        
        else:
            return render(request, 'user/password/otp_verification.html')
    else:
        # Clear session data if the state is not properly set
        request.session.flush()
        return redirect('forgot_password')  # Redirect if user didn't access this page after forgot_password

def reset_password(request):
    print("Welcome in RESET PASSWORD")
    # Check if user accessed this page after otp_verification
    if request.session.get('password_reset_state') == 'otp_verification':
        # Check if new password is submitted and update password
        if request.method == 'POST':
            reset_email = request.session.get('reset_email')
            p1 = request.POST.get('password1')
            p2 = request.POST.get('password2')
            
            if p1 == p2:
                # Retrieve the user using get() instead of filter()
                try:
                    user = User.objects.get(email=reset_email)
                    user.set_password(p1)
                    user.save()
                    
                    # Add success message
                    messages.success(request, 'Password successfully changed!')
                    
                    # Clear session data
                    request.session.flush()
                    print("password changes successful")
                    return redirect('user_login')
                except User.DoesNotExist:
                    # Add error message if user does not exist
                    messages.error(request, 'No user found with this email address.')
            else:
                # Add error message if passwords don't match
                messages.error(request, "Passwords don't match. Please try again.")
        
        
        return render(request, 'user/password/reset_password.html')
    else:
        # Clear session data if the state is not properly set
        request.session.flush()
        return redirect('forgot_password')  # Redirect if user didn't access this page after otp_verification

# ------------------------ EMAIL -----------------------------

import random
import string
from django.core.mail import send_mail
from django.conf import settings


def generate_otp(length=4):
    characters = string.digits
    otp = ''.join(random.choice(characters) for _ in range(length))
    return otp

# ============================================================

