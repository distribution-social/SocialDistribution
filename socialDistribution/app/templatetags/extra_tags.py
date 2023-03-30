# https://docs.djangoproject.com/en/4.1/howto/custom-template-tags/
from django import template
from ..models import *
import uuid
import json

register = template.Library()

@register.filter(name='classname')
def classname(obj):
  return obj.__class__.__name__

@register.filter(name='isRequest')
def is_request(user_id,id):
  user = Author.objects.get(id=id)
  return len(user.sent_requests.filter(id=user_id)) >= 1

@register.filter(name='isFollowing')
def is_following(user_id,id):
  user = Author.objects.get(id=id)
  return len(user.following.filter(id=user_id)) >= 1

@register.filter
def convert_username_to_id(value):
    return Author.objects.get(username=value).id
    
@register.filter
def extract_uuid(id):
    return id.split("/")[-1] 

@register.filter
def convert_uuid_to_hex(uuid_string):
  return uuid_string
  # try:
  #   # attempt to convert the string to a UUID object
  #   my_uuid = uuid.UUID(uuid_string)
    
  #   # if the conversion is successful, the string is a UUID in hexadecimal representation
  #   return my_uuid
    
  # except:
  #   # if the conversion fails, the string is not a UUID in hexadecimal representation
  #   return uuid


@register.filter
def convert_to_json(obj):
  # import pdb; pdb.set_trace()
  # Convert the dictionary to a JSON string
  json_string = json.dumps(obj, default=str)

  # # Replace "False" with "false" in the JSON string
  # json_string = json_string.replace("False", "false")
  return json_string