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


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            display_name = form.cleaned_data.get('display_name')
            first_name, last_name = display_name.split()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            github = form.cleaned_data.get('github_username')
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')

            try:
                u = User.objects.create_user(
                    username, email, password, first_name=first_name, last_name=last_name)
            except Exception as e:
                return HttpResponse(e)
            else:
                u.save()

            try:
                Author.objects.create(host="127.0.0.1:8000", displayName=display_name, github=f"https://github.com/{github}",
                                      profileImage="photos123.google.com", email=email, username=username)
            except Exception as e:
                return HttpResponse(e)

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('home'))
            else:
                return redirect(reverse('signup'))
        else:
            return redirect(reverse('signup'))

    elif request.method == "GET":
        context = {"title": "signup", "form": SignupForm()}
        return render(request, 'signup.html', context)


@require_http_methods(["GET"])
@login_required(login_url="/login")
def home(request):
    user = request.user
    return HttpResponse(f"Hello {user.first_name} {user.last_name}")


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
                return redirect(reverse('login'))
    elif request.method == "GET":
        context = {"title": "signin", "form": SigninForm()}
        return render(request, 'signin.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def signout(request):
    if request.method == "GET":
        logout(request)
        return redirect(reverse('home'))
