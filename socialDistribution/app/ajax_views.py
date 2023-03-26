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
from urllib.parse import urljoin

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
        headers={}
        if foreignNode.username:
            headers = {
                    'Authorization': f"Basic {foreignNode.getToken()}",
                    'Content-Type': 'application/json'
            }


        params = {
            'page': '1',
            'size': '20'
        }

        try:
            url = urljoin(base_url,'authors')
            res = requests.get(url, headers=headers, params=params)

            authors = json.loads(res.text)
            # if base_url == "https://peer2pressure.herokuapp.com/":
            #         import pdb; pdb.set_trace()
            print(authors['items'])
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
                url = urljoin(base_url,f'authors/{uuid}/posts')
                res = requests.get(url,headers=headers)

                author_posts = json.loads(res.text)
                for post in author_posts['items']:
                    # if base_url == "https://peer2pressure.herokuapp.com/":
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

                    post['tag'] = foreignNode.nickname
                    allPosts.append(post)
        except Exception as e:
            print(base_url,e)

    return JsonResponse({'posts': allPosts})

@login_required(login_url="/login")
@require_http_methods(["GET"])
def post_details(request):

    post_uuid = request.GET.get("uuid")
    post_obj = Post.objects.get(uuid=post_uuid)

    host =  post_obj.made_by.host
    author = post_obj.made_by

    if not host.endswith('/'):
        host += '/'

    # if not "https" in host:
    #     host = host.replace("http", "https")

    foreignNode = ForeignAPINodes.objects.get(base_url=host)
    headers={}
    if foreignNode.username:
        headers = {
                'Authorization': f"Basic {foreignNode.getToken()}",
                'Content-Type': 'application/json'
        }

    params = {

    }
    try:
        res = requests.get(post_obj.origin, headers=headers)
    except Exception as e:
        response = JsonResponse({'error': str(e)})
        response.status_code = 500
        return response
    post = json.loads(res.text)

    post['tag'] = foreignNode.nickname

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