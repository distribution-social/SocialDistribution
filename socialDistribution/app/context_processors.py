from django.contrib.auth.models import User
from .models import Author
from .API.serializers import AuthorSerializer
from  django.http import JsonResponse
from django.core import serializers
import json

def current_author(request):
  try:
    author = Author.objects.get(username=request.user.username)
    serializer = AuthorSerializer(author,context={'request':request,'kwargs':{}})
    return {'current_author': json.dumps(serializer.data)}
  except Exception as e:
    author = None
  return {'current_author': author}