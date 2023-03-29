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
    print(json.loads(serializer.data))
    return {'current_author': json.loads(serializer.data)}
  except Exception as e:
    author = None
  return {'current_author': author}