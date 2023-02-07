from django.shortcuts import render

from django.http import HttpResponse

from .forms import SignupForm


def signup(request):
    context = {"title": "signup", "form": SignupForm()}
    return render(request, 'signup.html', context)
