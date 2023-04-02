from django.http import HttpResponse
from django.template.loader import render_to_string
import json
from .forms import CommentForm


def get_post_card_template(request):
    post_data = request.body
    if post_data:
        context = {'user': request.user,'post': json.loads(post_data), "comment_form": CommentForm()}
        html = render_to_string('post_card.html', context)
        return HttpResponse(html)
    else:
        return HttpResponse('Error: Missing post data')
    

def get_post_details_template(request):
    post_data = request.body
    if post_data:
        context = {'user': request.user,'post': json.loads(post_data), "comment_form": CommentForm()}
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