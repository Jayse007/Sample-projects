from django.shortcuts import render, redirect
from .models import *
from .forms import RoomForm
from django.db.models import Q
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse

def loginPage(request):
    page = 'login'
    
    if request.user.is_authenticated:
        return redirect('home')

    if request.POST:
        username = request.POST['username'].lower()
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        
        else:
            return render(request, 'base/login_register.html', {'message':"This user does not exist. Please check username and password"})
        
    context = {'page': page}
    
    return render(request, 'base/login_register.html', context)
     
def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form = UserCreationForm()
    if request.POST:
        form = UserCreationForm(request.POST)
        if form.is_valid:
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        
        else:
            return HttpResponse('An error occurred during this registration')


    return render(request, 'base/login_register.html', {'form':form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q))
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context= {'rooms': rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
   
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(pk=pk)
    messages = room.messages.all()
    participants = room.participants.all() 

    if request.POST:
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST['body']
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)       

    context = {'room': room, 'messages': messages, 'participants':participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(pk=pk)
    rooms = user.rooms.all()
    room_messages = user.messages.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms': rooms, 'room_messages': room_messages, 'topics':topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.POST:
        form = RoomForm(request.POST) 
        if form.is_valid():
           room = form.save(commit=False)
           room.host =request.user
           room.save()
           return redirect('home')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(pk=pk)
    form = RoomForm(instance=room)
    
    if request.user != room.host:
        return HttpResponse("You are not allowed here.")

    if request.POST:
        form = RoomForm(request.POST, instance= room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room= Room.objects.get(pk=pk)
    if request.user != room.host:
        return HttpResponse("You are not allowed here.")
    
    if request.POST:
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(pk=pk)
    if request.user != message.user:
        return HttpResponse("You are not allowed here.")
    
    if request.POST:
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})