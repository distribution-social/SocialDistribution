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
from posixpath import join as urljoin

from django.contrib.auth.models import User
from .helpers import *
from django.db.models import Q
# import pdb
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
            'size': '10'
        }

        try:
            # if base_url == "https://bigger-yoshi.herokuapp.com/api/":
            #     import pdb; pdb.set_trace()
            url = urljoin(base_url,'authors')
            res = requests.get(url, headers=headers, params=params)

            authors = json.loads(res.text)
           

            for author in authors['items']:
                try:
                    if author['id']:
                        uuid = author['id'].split("/")[-1]
                        author_exists = Author.objects.filter(id=uuid).exists()

                        if not "displayName" in author:
                            author['displayName'] = "displayName typo on other team"

                        if not author_exists:
                            author_obj = standardize_author(author)
                            author_obj['id'] = uuid
                            author_obj['confirmed'] = True

                            if not author['github']:
                                author['github'] = ''


                            Author.objects.create(**author_obj,username=uuid)
                except Exception as e:
                    # pdb.set_trace()
                    continue

                try:
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
                                # pdb.set_trace()
                                print(f"creating post failed in ajax {post_obj['uuid']}: {e}")

                       
                        try:
                            like_url = urljoin(url,f'{uuid}/likes')
                            res = requests.get(like_url,headers=headers)
                            post['likeCount'] = len(json.loads(res.text)['items'])
                        except Exception as e:
                            print(f'Error getting like of post {like_url}: {e}')
                            post['likeCount'] = 0

                        post['tag'] = foreignNode.nickname
                        post['auth_token'] = foreignNode.getToken()


                        #temp for now, as some teams are not returning
                        if 'count' not in post:
                            post['count'] = 0

                        if 'commentSrc' not in post:
                            #Bigger yoshi is sending comments as list when it should be url, next line breaks.
                            try:
                                comments = requests.get(post['comments'], headers=headers)
                                post['commentSrc'] = json.loads(comments.text)
                        
                                #yosh is hardcoding so a work arond
                                post['count'] = len(post['commentSrc']['comments'])
                            except:
                                post['commentSrc'] = []

                        # if base_url == "https://bigger-yoshi.herokuapp.com/api/":
                        #     import pdb; pdb.set_trace()
                        allPosts.append(post)
                except Exception as e:
                    # pdb.set_trace()
                    print('errors')
        except Exception as e:
            # pdb.set_trace()
            print("error here with author url")
            
        # except Exception as e:
        #     import pdb; pdb.set_trace()
        #     print(base_url,e)

    return JsonResponse({'posts': allPosts})

@login_required(login_url="/login")
@require_http_methods(["GET"])
def post_details(request):

    post_uuid = request.GET.get("uuid")
    post_obj = Post.objects.get(uuid=post_uuid)

    host =  post_obj.made_by.host
    author = post_obj.made_by

    # if not host.endswith('/'):
    #     host += '/'
    # import pdb; pdb.set_trace()

    arr = host.split(":")
    arr[0] ='http'
    httpHost = ":".join(arr)
    arr[0] ='https'
    httpsHost = ":".join(arr)
    foreignNode = None
    try:
        foreignNode = ForeignAPINodes.objects.get(base_url=httpHost)
    except:
        try:
            foreignNode = ForeignAPINodes.objects.get(base_url=httpsHost)
        except:
            print("Something wrong w foreign node")

    
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
    url = urljoin(post_obj.origin,f'likes')
    try:
        res = requests.get(url,headers=headers)
        post['likeCount'] = len(json.loads(res.text)['items'])
    except Exception as e:
        print(f'Error getting like of post {post_obj.origin}: {e}')
        post['likeCount'] = 0
    post['tag'] = foreignNode.nickname
    post['auth_token'] = foreignNode.getToken()

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