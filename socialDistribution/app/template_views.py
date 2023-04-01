from django.http import HttpResponse
from django.template.loader import render_to_string
import json
from .forms import CommentForm
from django import template
register = template.Library()
from django.utils.safestring import mark_safe
import markdown


@register.filter
def markdownify(value):
    md = markdown.Markdown(extensions=['markdown.extensions.fenced_code', 'markdown.extensions.tables', 'markdown.extensions.codehilite', 'markdown.extensions.toc', 'markdown.extensions.extra'])
    return mark_safe(md.convert(value))


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