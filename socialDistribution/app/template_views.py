from django.http import HttpResponse
from django.template.loader import render_to_string
import json
from .forms import CommentForm
from .models import *
from django.contrib.auth import get_user


def get_post_card_template(request):
    post_data = request.body
    author = Author.objects.get(username=request.user.username)
    followers = author.followers.all()
    
    # jsonFollowers = json.loads(followers)
    jsonFollowers = []
    for follower in followers:
        arr = follower.host.split(":")
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
                # import pdb; pdb.set_trace()
                print("Something wrong w foreign node")

       
        auth_token = ''
        if foreignNode.username:
            auth_token = foreignNode.getToken()

        jsonFollowers.append({
            'obj': follower,
            'auth_token': auth_token,
            'url': follower.url
        })

    if post_data:
        context = {'user': request.user,'post': json.loads(post_data), 'followers': jsonFollowers, "comment_form": CommentForm()}
        html = render_to_string('post_card.html', context)
        return HttpResponse(html)
    else:
        return HttpResponse('Error: Missing post data')

def get_post_details_template(request):
    post_data = request.body
    author = Author.objects.get(username=request.user.username)
    followers = author.followers.all()
    if post_data:
        context = {'user': request.user,'post': json.loads(post_data), 'followers': followers, "comment_form": CommentForm()}
        html = render_to_string('post_card.html', context)
        return HttpResponse(html)
    else:
        return HttpResponse('Error: Missing post data')

def get_comment_template(request):
    comment = request.body
  
    if comment:
        context = {'user': request.user,'comment': json.loads(comment), "comment_form": CommentForm()}
        html = render_to_string('comment.html', context)
        return HttpResponse(html)
    else:
        return HttpResponse('Error: Missing post data')