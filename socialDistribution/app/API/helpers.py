from django.urls import reverse, resolve
from urllib.parse import urlparse

def get_full_uri(request,view_name,kwargs={},remove_str='') -> str:
  return str(request.build_absolute_uri(reverse(view_name, kwargs=kwargs))).replace(remove_str,'')

def get_values_from_uri(path,add_api=False):
  parsed_uri = urlparse(path)
  path = parsed_uri.path
  if add_api:
    path = f'/api{parsed_uri.path}'
  try:
    func, args, kwargs = resolve(path)
  except Exception as e:
    print(e)
    return {}
  return kwargs

def parse_values(path):
  parts = path.split('/')
  kwargs = {
    'author_id': None,
    'post_id': None,
    'comment_id': None,
    'follower_author_id': None,
  }
  for i in range(len(parts)-1):
    if parts[i] == 'authors':
      kwargs.update({'author_id': parts[i+1]})
    elif parts[i] == 'posts':
      kwargs.update({'post_id': parts[i+1]})
    if parts[i] == 'followers':
      kwargs.update({'follower_author_id': parts[i+1]})
    if parts[i] == 'comments':
      kwargs.update({'comment_id': parts[i+1]})
  return kwargs
