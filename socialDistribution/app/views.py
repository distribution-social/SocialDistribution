from django.shortcuts import render
from django.http import HttpResponse
from .forms import SignupForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

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

            user = User.objects.create_user(
                username, email, password)
            
            user.save()

            user = authenticate(username=username, password=password)
            
            login(request, user)
            # Redirect to home page
            # print(display_name, username, email, github_url, password)

        # print(request.POST.get("display_name"))
        return HttpResponse("Successfully signed up!")
    elif request.method == "GET":
        context = {"title": "signup", "form": SignupForm()}
        return render(request, 'signup.html', context)
