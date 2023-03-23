from django.shortcuts import render, redirect
from django.http import *
from .forms import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.contrib import messages
from django.core.serializers import *
import requests
from django.core import serializers
from django.http import JsonResponse
import json

from django.contrib.auth.models import User
from .helpers import *
from django.db.models import Q

@login_required(login_url="/login")
@require_http_methods(["GET"])
def posts(request):
    base_url = request.build_absolute_uri('/')
    print(base_url)
    user = request.user
    author = Author.objects.get(username=user.username)
    # posts1 = Post.objects.filter(visibility="PUBLIC")
    # posts2 = Post.objects.filter(visibility="FRIENDS", made_by__in=author.following.all())
    # posts = (posts1 | posts2).order_by('-date_published')


    allPosts = []

    #For now hardcoded, but when we get other nodes we have to look ForeignNodes model and do it for each
    # we can extract the token because its a attribute on the model.
    headers = {
            'Authorization': f"Basic c2VydmVyMzoxMjM=",
            'Content-Type': 'application/json'
    }

    params = {
        'page': '1',
        'size': '10'
    }

    try:
        res = requests.get(f'{base_url}api/authors', headers=headers, params=params)
        authors = json.loads(res.text)

        for author in authors['items']:
            uuid = str(author['id']).split("/")[-1]
            res = requests.get(f'{base_url}api/authors/{uuid}/posts',headers=headers)

            author_posts = json.loads(res.text)
            for post in author_posts['items']:
                allPosts.append(post)
    except:
        print(res)
        print(base_url)

    return JsonResponse({'posts': allPosts})

@login_required(login_url="/login")
@require_http_methods(["GET"])
def post_details(request):
    base_url = request.build_absolute_uri('/')
    author = Author.objects.get(username=request.user.username)
    post_uuid = request.GET.get("uuid")
    #TODO: when we get other team stuff we just have to look which host it is, and only call that server.
    #For now, I am testing using ours by hardcoding it.
    headers = {
            'Authorization': f"Basic c2VydmVyMzoxMjM=",
            'Content-Type': 'application/json'
    }

    params = {
        
    }
# 'api/authors/<uuid:author_id>/posts/<uuid:post_id>

    res = requests.get(f'{base_url}api/authors/{author.id}/posts/{post_uuid}', headers=headers)
    
    post = json.loads(res.text)

    return JsonResponse({'post': post})
