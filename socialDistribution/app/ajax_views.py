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
def explore_posts(request):

    foreignNodes = ForeignAPINodes.objects.all()
    user = request.user
    allPosts = []
    for foreignNode in foreignNodes:
        base_url = foreignNode.base_url
        print(base_url)


        headers = {
                'Authorization': f"Basic {foreignNode.getToken()}",
                'Content-Type': 'application/json'
        }


        params = {
            'page': '1',
            'size': '20'
        }

        try:
            res = requests.get(f'{base_url}authors', headers=headers, params=params)
            authors = json.loads(res.text)

            for author in authors['items']:
                if author['id']:
                    uuid = author['id'].split("/")[-1]
                    author_exists = Author.objects.filter(id=uuid).exists()

                    if not "displayName" in author:
                        author['displayName'] = "displayName typo on other team"

                    if not author_exists:
                        author_obj = standardize_author(author)
                        author_obj['id'] = uuid
                        author_obj['confirmed'] = True


                        Author.objects.create(**author_obj,username=uuid)

                uuid = str(author['id']).split("/")[-1]
                res = requests.get(f'{base_url}authors/{uuid}/posts',headers=headers)

                author_posts = json.loads(res.text)
                for post in author_posts['items']:
                    # if base_url == "https://yoshi-connect.herokuapp.com/":
                    #     import pdb; pdb.set_trace()
                    uuid = post['id'].split("/")[-1]

                    if not "title" in post:
                        post['title'] = f"title typo on other team {base_url}"

                    post_exists = Post.objects.filter(uuid=uuid).exists()

                    if not post_exists:
                        post_obj = standardize_post(post)
                        post_obj['uuid'] = uuid
                        author_id =  post['author']['id'].split("/")[-1]
                        post_obj['made_by'] = Author.objects.get(id=author_id)

                        # import pdb; pdb.set_trace()
                        try:
                            Post.objects.create(**post_obj)
                        except Exception as e:
                            print(f"creating post failed in ajax {post_obj['uuid']}: {e}")


                    allPosts.append(post)
        except Exception as e:
            print(base_url,e)

    return JsonResponse({'posts': allPosts})

@login_required(login_url="/login")
@require_http_methods(["GET"])
def post_details(request):
    # import pdb; pdb.set_trace()
    base_url = request.build_absolute_uri('/')
    author = Author.objects.get(username=request.user.username)
    post_uuid = request.GET.get("uuid")

    post_obj = Post.objects.get(uuid=post_uuid)

    #TODO: when we get other team stuff we just have to look which host it is, and only call that server.
    #For now, I am testing using ours by hardcoding it.
    headers = {
            'Authorization': f"Basic TmljazpXaWVsZ3Vz",
            'Content-Type': 'application/json'
    }

    params = {

    }

    res = requests.get(f'{base_url}api/authors/{author.id}/posts/{post_uuid}', headers=headers)

    post = json.loads(res.text)

    return JsonResponse({'post': post})


#utility functions (Refactor to diff file later)

def standardize_author(author):
    standardized_author = {k: v for k, v in author.items() if k in ['id', 'email', 'host','url', 'github', 'displayName', 'profileImage']}
    return standardized_author


def standardize_post(post):
    standardized_post = {k: v for k, v in post.items() if k in ['uuid','description', 'title', 'content', 'contentType','published', 'source', 'origin', 'visibility']}
    standardized_post.update({'date_published': standardized_post.pop('published')})
    standardized_post.update({'content_type': standardized_post.pop('contentType')})

    # standardized_post['made_by'] = post['author']['id'].split("/")[-1]
    return standardized_post