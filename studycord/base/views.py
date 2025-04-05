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

def registerUser(request):
    form = UserCreationForm()
    context = {'form': form}
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid(): 
            user = form.save(commit=False)
            user.username = user.username.lower() # make username lowercase
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Some error occured during registration")

    return render(request, 'base/login_register.html', context)

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

    if request.user != room.host: # only edit your own room
        return HttpResponse('You are not allowed here!')

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
def updateUser(request):
    context={}
    return render(request, 'base/update-user.html', context)