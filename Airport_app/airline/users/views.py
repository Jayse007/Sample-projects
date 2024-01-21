from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import CreateUserForm
# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    return render(request, "users/users.html")

def login_view(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        
        else:
            return render(request, "users/login.html"),{
                "message": "Please login with valid account details as this user does not exist."
            }
       
    return render(request, "users/login.html", ) 

def logout_view(request):
    logout(request)
    return render(request, "users/login.html", {
        "message": f"You have logged out successfully. Please, visit us again, "
    })

def signup(request):
    form = CreateUserForm()
    
    if request.method== "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('login'))
    return render(request, "users/signup.html", {'form':form})
    
