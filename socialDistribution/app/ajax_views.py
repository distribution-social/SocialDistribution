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
from datetime import datetime, timezone
from dateutil.parser import parse
from posixpath import join as urljoin
from urllib.parse import urlparse

from django.contrib.auth.models import User
from .helpers import *
from .API.helpers import *
from .API.serializers import *
from django.db.models import Q

import aiohttp
import asyncio
import sys

class URL():
    def __init__(self,url,method='get',headers=None,params=None,data=None):
        self.url = url
        self.method=method
        self.headers=headers
        self.params=params
        self.data=data

async def fetch_url(url:URL):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(url=url.url,method=url.method,headers=url.headers,params=url.params) as response:
                try:
                    return await response.json()
                except aiohttp.ContentTypeError:
                    # handle invalid JSON content
                    print(f"Invalid JSON content at URL: {url.url}")
                    return None
        except Exception as e:
            print(f'Error getting request: {url.url} - {str(e)}')
            return None

async def make_requests_async(url_list,future):
    loop = asyncio.get_running_loop()
    tasks = [loop.create_task(fetch_url(url)) for url in url_list]
    responses = await asyncio.gather(*tasks)
    future.set_result(responses)

def make_http_calls(url_list):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.Future()
    loop.create_task(make_requests_async(url_list,future))
    loop.run_until_complete(future)
    loop.close()
    return future.result()

def get_authors():
    foreignNodes = ForeignAPINodes.objects.all()
    urls = []
    for foreignNode in foreignNodes:
        base_url = foreignNode.base_url
        print(base_url)
        if foreignNode.username:
            headers = {
                    'Authorization': f"Basic {foreignNode.getToken()}",
                    'Content-Type': 'application/json'
            }
        params = {
            'page': '1',
            'size': '10000'
        }
        url = urljoin(base_url,'authors')
        urls.append(URL(url,'get',headers,params))
    responses = make_http_calls(urls)
    authors = []
    for response in responses:
        if response:
            try:
                authors.extend(response['items'])
            except KeyError:
                print(f'Skipping an authors response since it doesnt have items. {response}')
            except:
                pass
    return authors

def get_posts(authors):
    urls = []
    for author in authors:
        token = get_auth_token(author.get('url'))
        if not token:
            continue
        headers = {
            'Authorization': f"Basic {token}",
            'Content-Type': 'application/json'
        }
        url = urljoin(author['url'],'posts')
        urls.append(URL(url,'get',headers))
    responses = make_http_calls(urls)
    posts = []
    for response in responses:
        if response:
            try:
                posts.extend(response['items'])
            except KeyError:
                print(f'Skipping a posts response since it doesnt have items. {response}')
            except:
                pass
    for post in posts:
        post['auth_token'] = get_auth_token(post.get('origin'))
    return posts

def get_like_count(post):
    origin = post.get('origin')
    url = urljoin(origin,f'likes')
    if 'localhost' not in url:
        try:
            headers = {
                'Authorization': f"Basic {get_auth_token(post.get('author').get('url'))}",
                'Content-Type': 'application/json'
            }
            res = requests.get(url,headers=headers,timeout=2)
            post['likeCount'] = len(json.loads(res.text)['items'])
        except Exception as e:
            print(f'Error getting like of post {origin}: {e}')
            post['likeCount'] = 0
    else:
        print(f'Has local host:',post['id'])
        post['likeCount'] = 0
    return post

def filter_authors_following(actor,authors):
    urls = []
    try:
        actor_obj = Author.objects.get(username=actor.username)
    except:
        return []
    for author in actor_obj.following.all():
        urls.append(author.url)
    authors = [d for d in authors if d['url'] in urls]
    return authors

def filter_authors_profile(author_id,authors):
    authors = [d for d in authors if author_id in d['id']]
    return authors

def filter_posts(posts,visibility=['PUBLIC']):
    posts = [d for d in posts if d['visibility'] in visibility and not bool(d['unlisted'])]
    return posts

def sort_and_tag_posts(posts:list):
    posts.sort(key=lambda x: parse(str(x['published'])).replace(tzinfo=timezone.get_current_timezone()),reverse=True)
    for post in posts:
        post['tag'] = get_node_nickname(post['author']['host'])
        post['uuid'] = post['id'].split("/")[-1]
    return posts

def get_auth_token(url):
    parsed = urlparse(url)
    try:
        foreignNode = ForeignAPINodes.objects.get(base_url__contains=parsed.netloc)
    except:
        return None
    return foreignNode.getToken()

def get_node_nickname(host):
    try:
        foreignNode = ForeignAPINodes.objects.get(base_url__contains=host)
    except:
        return None
    return foreignNode.nickname

def get_node_host(nickname):
    try:
        foreignNode = ForeignAPINodes.objects.get(nickname=nickname)
    except:
        return None
    return foreignNode.base_url

@require_http_methods(["GET"])
def public_posts(request):
    authors = get_authors()
    posts = get_posts(authors)
    posts = filter_posts(posts)
    posts = sort_and_tag_posts(posts)
    context = {'user': request.user,'posts': posts, "comment_form": CommentForm()}
    return JsonResponse({'posts': posts})
    # return render(request, 'post_stream.html', context)

@login_required(login_url="/login")
@require_http_methods(["GET"])
def home_posts(request):
    authors = get_authors()
    authors = filter_authors_following(request.user,authors)
    posts = get_posts(authors)
    posts = filter_posts(posts,['PUBLIC','FRIENDS'])
    posts = sort_and_tag_posts(posts)
    context = {'user': request.user,'posts': posts, "comment_form": CommentForm()}
    return JsonResponse({'posts': posts})

@login_required(login_url="/login")
@require_http_methods(["GET"])
def profile_posts(request,author_id):
    authors = get_authors()
    authors = filter_authors_profile(author_id,authors)
    posts = get_posts(authors)
    posts = filter_posts(posts,['PUBLIC','FRIENDS'])
    posts = sort_and_tag_posts(posts)
    context = {'user': request.user,'posts': posts, "comment_form": CommentForm()}
    return JsonResponse({'posts': posts})

@login_required(login_url="/login")
@require_http_methods(["GET"])
def post_details(request,node,author_id,post_id):
    url = urljoin(get_node_host(node),'authors',author_id,'posts',post_id)
    headers = {
        'Authorization': f"Basic {get_auth_token(get_node_host(node))}",
        'Content-Type': 'application/json'
    }
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            raise Exception('Post not found.')
    except Exception as e:
        response = JsonResponse({'error': str(e)})
        response.status_code = 500
        return response
    post = json.loads(res.text)
    url = urljoin(post.get('origin'),f'likes')
    origin = post.get('origin')
    if not post.get('likeCount'):
        post = get_like_count(post)
    post['tag'] = node
    post['uuid'] = post['id'].split("/")[-1]
    context = {'user': request.user,'post': post, "comment_form": CommentForm()}
    return render(request,'post_detail.html',context)


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