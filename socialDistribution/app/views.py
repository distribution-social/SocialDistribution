from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SignupForm, SigninForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Author
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User

def username_exists(username):
    return User.objects.filter(username=username).exists()

def email_address_exists(email):
    return User.objects.filter(email=email).exists()

def github_exists(github):
    return Author.objects.filter(github=f"https://github.com/{github}").exists()

def is_valid(request, username, email, github, password, confirm_password):
    if username_exists(username):
        messages.warning(request, "Username is not available.")
        return False

    elif email_address_exists(email):
        messages.warning(request, "Email address is already in use.")
        return False
    
    elif github_exists(github):
        messages.warning(request, "Github username is already in use.")
        return False

    elif password != confirm_password:
        messages.warning(request, "Passwords do not match.")
        return False

    else:
        return True

@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            display_name = form.cleaned_data.get('display_name')
            try:
                first_name, last_name = display_name.split()
            except ValueError:
                first_name = display_name
                last_name = ""

            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            github = form.cleaned_data.get('github')
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')

            if not is_valid(request, username, email, github, password, confirm_password):
                return redirect(reverse('signup'))

            try:
                u = User.objects.create_user(
                    username, email, password, first_name=first_name, last_name=last_name)
            except Exception as e:
                messages.warning(request, e)
                return redirect(reverse('signup'))
            else:
                u.save()

            try:
                Author.objects.create(host="127.0.0.1:8000", displayName=display_name, github=f"https://github.com/{github}",
                                      profileImage=None, email=email, username=username)
            except Exception as e:
                messages.warning(request, e)
                return redirect(reverse('signup'))

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('home'))
            else:
                return redirect(reverse('signup'))
        else:
            return redirect(reverse('signup'))

    elif request.method == "GET":
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        else:
            context = {"title": "signup", "form": SignupForm()}
            return render(request, 'signup.html', context)


@require_http_methods(["GET"])
@login_required(login_url="/login")
def home(request):
    user = request.user
    context = {"user": user}
    return render(request, 'home.html', context)

@require_http_methods(["GET", "POST"])
def signin(request):
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('home'))
            else:
                messages.warning(request, "Invalid username or password")
                return redirect(reverse('login'))
    elif request.method == "GET":
        # No need to sign in again
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        else:
            context = {"title": "signin", "form": SigninForm()}
            return render(request, 'signin.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def signout(request):
    if request.method == "GET":
        logout(request)
        return redirect(reverse('home'))

