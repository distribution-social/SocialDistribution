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
from .API.helpers import *
from django.db.models import Q


import aiohttp
import asyncio
loop = asyncio.get_event_loop()

class URL():
    def __init__(self,url,method='get',headers=None,params=None,data=None):
        self.url = url
        self.method=method
        self.headers=headers
        self.params=params
        self.data=data

async def fetch_url(url:URL):

    async with aiohttp.ClientSession() as session:
        async with session.request(url=url.url,method=url.method,headers=url.headers,params=url.params) as response:
            try:
                return await response.json()
            except aiohttp.ContentTypeError:
                # handle invalid JSON content
                print(f"Invalid JSON content at URL: {url.url}")
                return None

async def make_requests_async(url_list):
    tasks = [asyncio.create_task(fetch_url(url)) for url in url_list]
    responses = await asyncio.gather(*tasks)
    return responses

def make_http_calls(loop:asyncio.AbstractEventLoop,url_list):
    return loop.run_until_complete(make_requests_async(url_list))

def get_authors(loop:asyncio.AbstractEventLoop):
    foreignNodes = ForeignAPINodes.objects.all()
    urls = []
    for foreignNode in foreignNodes:
        base_url = foreignNode.base_url
        if foreignNode.username:
            headers = {
                    'Authorization': f"Basic {foreignNode.getToken()}",
                    'Content-Type': 'application/json'
            }
        params = {
            'page': '1',
            'size': '100'
        }
        url = urljoin(base_url,'authors')
        urls.append(URL(url,'get',headers,params))
    responses = make_http_calls(loop,urls)
    authors = []
    for response in responses:
        if response:
            authors.extend(response['items'])
    return authors

def get_auth_header(host):
    try:
        foreignNode = ForeignAPINodes.objects.get(base_url=host)
    except:
        return None
    return foreignNode.getToken()

def get_node_nickname(host):
    try:
        foreignNode = ForeignAPINodes.objects.get(base_url=host)
    except:
        return None
    return foreignNode.nickname

@require_http_methods(["GET"])
def public_posts(request):
    authors = get_authors(loop)
    urls = []
    for author in authors:
        token = get_auth_header(author['host'])
        if not token:
            continue
        headers = {
            'Authorization': f"Basic {token}",
            'Content-Type': 'application/json'
        }
        url = urljoin(author['url'],'posts')
        urls.append(URL(url,'get',headers))
    responses = make_http_calls(loop,urls)
    posts = []
    for response in responses:
        if response:
            posts.extend(response['items'])
    posts = [d for d in posts if d['visibility'] in ['PUBLIC']]
    posts = sorted(posts, key=lambda d: d['published'],reverse=True)
    # for post in posts:
    #     post['tag'] = get_node_nickname(post['author']['host'])
    return JsonResponse({'posts': posts})

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
    url = urljoin(post_obj.origin,f'likes')
    try:
        res = requests.get(url,headers=headers)
        post['likeCount'] = len(json.loads(res.text)['items'])
    except Exception as e:
        print(f'Error getting like of post {post_obj.origin}: {e}')
        post['likeCount'] = 0
    post['uuid'] = parse_values(post['url']).get('post_id')
    post_obj['made_by'] = post['author']
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