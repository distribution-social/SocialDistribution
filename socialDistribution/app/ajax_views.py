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

    foreignNodes = ForeignAPINodes.objects.all()
    user = request.user

    for foreignNode in foreignNodes:
        base_url = foreignNode.base_url
        print(base_url)
      
        # author = Author.objects.get(username=user.username)
        # posts1 = Post.objects.filter(visibility="PUBLIC")
        # posts2 = Post.objects.filter(visibility="FRIENDS", made_by__in=author.following.all())
        # posts = (posts1 | posts2).order_by('-date_published')


        allPosts = []
        headers = {}

        if foreignNode.username:
            headers = {
                    'Authorization': f"Basic {foreignNode.getToken()}",
                    'Content-Type': 'application/json'
            }
        

        params = {
            'page': '1',
            'size': '5'
        }

        try:
            res = requests.get(f'{base_url}authors', headers=headers, params=params)
            authors = json.loads(res.text)

            for author in authors['items']:
                uuid = str(author['id']).split("/")[-1]
                res = requests.get(f'{base_url}authors/{uuid}/posts',headers=headers)

                author_posts = json.loads(res.text)
                import pdb; pdb.set_trace()
                for post in author_posts:
             
                    import pdb; pdb.set_trace()
                    

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
