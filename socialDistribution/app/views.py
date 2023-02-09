from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SignupForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

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
            user = authenticate(username=username, password=password)
            
            login(request, user)
            return redirect("/home")

    elif request.method == "GET":
        context = {"title": "signup", "form": SignupForm()}
        return render(request, 'signup.html', context)

@login_required
def home(request):
    return HttpResponse("Homepage")

def signin(request):
    return HttpResponse("LoginPage")
