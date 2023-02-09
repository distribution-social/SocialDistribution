from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SignupForm, SigninForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Author

def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            display_name = form.cleaned_data.get('display_name')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            github_url = form.cleaned_data.get('github_url')
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')
            u = User.objects.create_user(
                username, email, password)
            
            u.save()

            Author.objects.create(host="127.0.0.1:8000", displayName=display_name, github=github_url, profileImage="www.google.com", email=email, username=username)

            user = authenticate(username=username, password=password)


            
            login(request, user)
        return redirect("/home")

    elif request.method == "GET":
        context = {"title": "signup", "form": SignupForm()}
        return render(request, 'signup.html', context)

@login_required(login_url="/signin")
def home(request):
    return HttpResponse("Homepage")

def signin(request):
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
        return redirect("/home")
    elif request.method == "GET":
        context = {"title": "signin", "form": SigninForm()}
        return render(request, 'signin.html', context)

@login_required
def signout(request):
    if request.method == "GET":
        logout(request)
        return redirect('/home')

