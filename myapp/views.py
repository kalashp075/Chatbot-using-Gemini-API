from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import random
from django.contrib import auth
from django.contrib.auth.decorators import login_required
import re  # Regular expression module
from .models import Profile
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import authenticate
import uuid
from django.utils.dateparse import parse_date
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Chat
from django.utils import timezone
import google.generativeai as genai

genai.configure(api_key="GEMINI_API_KEY")

# Create your views here.
def myapp(request):
    return render(request, "login_page.html")

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username is None or password is None:
            messages.error(request, 'Both Username and password are required.')
            return redirect('login_page')

        # Authenticate user
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)  # Log the user in
            return redirect('home_page')  # Redirect to home page after successful login
        else:
            messages.error(request, 'Invalid username or password')  # Show error message
            return redirect('login_page')

    return render(request, "login_page.html")

def signup_page1(request):
    if request.method == 'POST':
        email = request.POST['email']

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Invalid email format.')
            return redirect('signup_page1')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken')
            return redirect('signup_page1')
        else:
            request.session['email'] = email
            return redirect('signup_page2')

    return render(request, "signup_page1.html")

def signup_page2(request):
    email = request.session.get('email', '')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if not username or not password:
            messages.error(request, 'Both username and password are required.')
            return redirect('signup_page2')

        # Validate username criteria
        if not re.match(r'^[a-zA-Z0-9_]{3,30}$', username):  # Adjust regex as needed
            messages.error(request, 'Username must be alphanumeric and 3-30 characters long.')
            return redirect('signup_page2')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken. Please choose a different username.')
            return redirect('signup_page2')

        request.session['username'] = username
        request.session['password'] = password
        return redirect('signup_page3')
    
    return render(request, 'signup_page2.html', {'message': email})

def signup_page3(request):
    if request.method == 'POST':
        fullname = request.POST['fullname']
        birthdate = request.POST['birthdate']
        email = request.session.get('email', '')
        password = request.session.get('password', '')
        username = request.session.get('username', '')

        if not email or not password or not username:
            messages.error(request, "Session expired. Please restart the signup process.")
            return redirect('signup_page1')

        # Generate a verification code
        verification_code = str(random.randint(100000, 999999))
        
        # Store the verification code and other details in the session
        request.session['verification_code'] = verification_code
        request.session['fullname'] = fullname
        request.session['birthdate'] = birthdate

        # Send the verification email
        send_mail(
            'Your Verification Code',
            f'Your verification code is {verification_code}.',
            'youremail@gmail.com',  # Replace with your email
            [email],
            fail_silently=False,
        )
        
        return redirect('verification')

    return render(request, "signup_page3.html")

def verification(request):
    # Check if required session data is available
    if 'verification_code' not in request.session or not request.session.get('email', ''):
        messages.error(request, "Verification process not started or session expired.")
        return redirect('signup_page1')

    if request.method == 'POST':
        input_code = request.POST.get('input')
        verification_code = request.session.get('verification_code', '')

        if input_code == verification_code:
            # Retrieve session data
            email = request.session.get('email', '')
            password = request.session.get('password', '')
            username = request.session.get('username', '')
            fullname = request.session.get('fullname', '')
            birthdate = request.session.get('birthdate', '')

            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password)
            
            # Create a Profile instance and save fullname and birthdate
            Profile.objects.create(user=user, fullname=fullname, birthdate=birthdate)

            # Completely clear the session after user creation
            request.session.flush()

            # Log a success message
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login_page')
        else:
            messages.error(request, 'Invalid verification code. Please try again.')
            return redirect('verification')

    # Render the verification page with the email to be verified
    email = request.session.get('email', '')
    return render(request, "verification.html", {'email': email})

def resend_verification(request):
    # Retrieve the email from the session
    email = request.session.get('email', '')

    if email:
        # Generate a new verification code
        verification_code = str(random.randint(100000, 999999))

        # Update the session with the new verification code
        request.session['verification_code'] = verification_code

        # Resend the email
        send_mail(
            'Your New Verification Code',
            f'Your new verification code is {verification_code}.',
            'youremail@gmail.com',  # Replace with your email
            [email],
            fail_silently=False,
        )

        messages.info(request, 'A new verification code has been sent to your email.')
    else:
        messages.info(request, 'Session expired. Please sign up again.')
        return redirect('signup_page1')

    return redirect('verification')


def landing(request):
    return render(request, "landing.html")

def logout_view(request):
    auth.logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('landing')

@login_required
def profile_page(request):
    return render(request, 'profile_page.html')

@login_required
def home_page(request):
    # Fetch user-specific history
    chats = Chat.objects.filter(user=request.user)
    return render(request, "home_page.html", {'chats': chats})

def ai_interaction(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        if not message:
            return JsonResponse({'error': 'Message cannot be empty.'})

        response = ask_gemini(message)

        if response is None or response.strip() == '':
            return JsonResponse({'error': 'No response from AI service'}, status=500)

        if "rate limit" in response.lower():
            return JsonResponse({'error': 'Rate limit exceeded. Please try again later.'}, status=429)

        # Save the chat message and response to the database
        chat = Chat(user=request.user, message=message, response=response, created_at=timezone.now())
        chat.save()

        # Return the message and response as JSON
        return JsonResponse({'message': message, 'response': response})

    # If not a POST request, just render the home page with chat history
    chats = Chat.objects.filter(user=request.user)
    return render(request, 'home_page.html', {'chats': chats})


def ask_gemini(message):
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(message)
    return response.text


