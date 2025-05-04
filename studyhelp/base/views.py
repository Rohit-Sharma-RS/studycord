from django.shortcuts import render, redirect
from .forms import RoomForm
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, User, Message
from .forms import RoomForm, UserForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Profile
from .utils import send_verification_email
from django.core.mail import send_mail
from django.http import HttpResponse

# rooms = [
#     {'id': 1, 'name': "Let's learn python"},
#     {'id': 2, 'name': "Code with me"}
# ]

def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=="POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User does not exist")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username or password does not exist")
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

# Update in your views.py file


def registerUser(request):
    form = UserCreationForm()
    
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid(): 
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.is_active = True  # Allow login but track verification separately
            user.email = request.POST.get('email')  # Make sure to add email field to your form
            user.save()
            
            # Create user profile with verification token
            profile = Profile.objects.create(user=user)
            
            # Send verification email
            send_verification_email(user, profile.verification_token, request)
            
            messages.success(
                request, 
                "Registration successful! Please check your email to verify your account."
            )
            
            return redirect('login')
        else:
            messages.error(request, "Some error occurred during registration")
    
    context = {'form': form}
    return render(request, 'base/login_register.html', context)

def verify_email(request, token):
    try:
        profile = Profile.objects.get(verification_token=token)
        if not profile.email_verified:
            profile.email_verified = True
            profile.save()
            messages.success(request, "Your email has been verified successfully! You can now log in.")
        else:
            messages.info(request, "Your email was already verified.")
        
        return redirect('login')
    except Profile.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect('login')

def logoutPage(request):
    logout(request)
    return redirect('home')

def home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)| # query upwards to parent for topic name.
        # __icontains is case insensitive
        # __contains is case sensitive
        Q(name__icontains=q)|
        Q(description__icontains=q) # query for description
    )
    topic = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.all().order_by('-created')[:3] # get last 3 messages
    context= {'rooms': rooms, 'topics': topic, 'room_count': room_count, 'room_messages': room_messages}
    return render(  request, 'base/home.html', context)

def room(request, pk):
    try:
        room = Room.objects.get(id=pk)
        room_messages = room.message_set.all().order_by('-created')
        participants = room.participants.all()
        
        if request.method == "POST" and request.user.is_authenticated:
            body = request.POST.get('body')
            
            if body and body.strip():  # Check if body has content after stripping whitespace
                message = Message.objects.create(
                    user=request.user,
                    room=room,
                    body=body
                )
                
                # Only add the user as a participant if they're not already one
                if request.user not in participants:
                    room.participants.add(request.user)
                
                # Redirect to clear the form and prevent double submissions
                return redirect('room', pk=room.id)
        
        context = {
            'room': room, 
            'room_messages': room_messages, 
            'participants': participants,
        }
        
        return render(request, 'base/room.html', context)
        
    except Room.DoesNotExist:
        # Handle the case where the room doesn't exist
        return redirect('home')  # Or whatever your home URL name is

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all() # get all rooms created by user
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context={'user':user, 'rooms': rooms, 
             'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='/login') # only logged in users can create room
def createRoom(request):
    form = RoomForm()
    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login') # only logged in users can delete room
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='/login') # only logged in users can delete room
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse('You are not allowed here!')
    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})

def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here!')
    form  = RoomForm(instance=room)
    if request.method=="POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    # form = RoomForm(request.POST, instance=room)
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login') # only logged in users can delete room
def updateUser(request, pk):
    user = request.user
    form = UserForm(instance=user)
    if request.method=="POST":
        form = UserForm(request.POST, instance=user) # instance=user to update the user in place
        # form = UserForm(request.POST) # this creates a new user instead of updating the existing one
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    context={'form': form}
    return render(request, 'base/update-user.html', context)


from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import PasswordReset
from .utils import send_password_reset_email

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')
        print(f"Password reset requested for email: {email}")
        
        try:
            user = User.objects.get(email=email)
            print(f"User found: {user.username}")
            
            # Create reset token
            reset_token = PasswordReset.objects.create(user=user)
            print(f"Reset token created: {reset_token.token}")
            
            # Send reset email
            email_sent = send_password_reset_email(user, reset_token.token, request)
            
            if email_sent:
                print("Email appears to have been sent successfully")
            else:
                print("Email sending appears to have failed")
            
            messages.success(
                request, 
                "If an account with that email exists, we've sent password reset instructions."
            )
            return redirect('login')
        except User.DoesNotExist:
            print(f"No user found with email: {email}")
            # For security, don't reveal if email exists or not
            messages.success(
                request, 
                "If an account with that email exists, we've sent password reset instructions."
            )
            return redirect('login')
    
    return render(request, 'base/forgot_password.html')

def test_email(request):
    """A simple view to test email functionality."""
    try:
        result = send_mail(
            subject='Test Email',
            message='This is a test email from your Django application.',
            from_email='vampire.instinct777@gmail.com',
            recipient_list=['pavankpawankpavan@gmail.com'],  # Replace with your email
            fail_silently=False,
        )
        return HttpResponse(f"Email test completed. Result: {result}")
    except Exception as e:
        return HttpResponse(f"Email test failed: {str(e)}")

def reset_password(request, token):
    try:
        reset_token = PasswordReset.objects.get(token=token)
        
        if not reset_token.is_valid():
            messages.error(request, "This password reset link has expired or already been used.")
            return redirect('forgot-password')
        
        if request.method == "POST":
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'base/reset_password.html')
            
            # Update user's password
            user = reset_token.user
            user.password = make_password(password)
            user.save()
            
            # Mark token as used
            reset_token.used = True
            reset_token.save()
            
            messages.success(request, "Your password has been reset successfully. You can now log in.")
            return redirect('login')
        
        return render(request, 'base/reset_password.html')
        
    except PasswordReset.DoesNotExist:
        messages.error(request, "Invalid password reset link.")
        return redirect('forgot-password')
    
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Profile
from .utils import send_verification_email
from .forms import CustomUserCreationForm  # Import your custom form

def registerUser(request):
    form = CustomUserCreationForm()  # Use custom form
    
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)  # Use custom form
        if form.is_valid(): 
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.is_active = True  # Allow login but track verification separately
            user.save()
            
            # Create user profile with verification token
            profile = Profile.objects.create(user=user)
            
            # Send verification email
            send_verification_email(user, profile.verification_token, request)
            
            messages.success(
                request, 
                "Registration successful! Please check your email to verify your account."
            )
            
            return redirect('login')
        else:
            messages.error(request, "Some error occurred during registration")
    
    context = {'form': form}
    return render(request, 'base/login_register.html', context)