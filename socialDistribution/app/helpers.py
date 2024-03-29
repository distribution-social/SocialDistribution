from django.contrib.auth.models import User
from .models import *
from django.contrib import messages
from app.models import *
import requests
from requests.auth import HTTPBasicAuth


def username_exists(username):
    return User.objects.filter(username=username).exists()


def email_address_exists(email):
    return User.objects.filter(email=email).exists()


def github_exists(github):
    return Author.objects.filter(github=f"https://github.com/{github}").exists()


def is_valid_info(request, username, email, github, password, confirm_password):
    if username_exists(username):
        messages.warning(request, "Username is not available.")
        return False

    elif email_address_exists(email):
        messages.warning(request, "Email address is already in use.")
        return False

    # elif github_exists(github):
    #     messages.warning(request, "Github username is already in use.")
    #     return False

    elif password != confirm_password:
        messages.warning(request, "Passwords do not match.")
        return False

    else:
        return True


def add_to_inbox(from_author,to,type,object):
    if from_author != to:
        activity = Activity.objects.create(type=type,content_object=object)
        return Inbox.objects.create(from_author=from_author,to=to,object=activity)
    return None

def convert_username_to_id(username):
    return Author.objects.get(username=username).id

def get_foreign_API_node(host):
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

    return foreignNode


def send_post_request(type, actor, object):

    foreign_api_node = ForeignAPINodes.objects.get(base_url=actor.host)
    username = foreign_api_node.username
    password = foreign_api_node.password
    # token = f"{foreign_api_node.username}:{foreign_api_node.password}"

    print("*" * 1000, username, password)

    headers = {
            'Content-Type': 'application/json'
    }

    json = {
        "type": type,
        "summary": f"{actor.displayName} {type}ed {object.displayName}'s request",
        "actor": {
            "type": "author",
            "id": actor.url,
            "url": actor.url,
            "host": actor.host,
            "displayName": actor.displayName,
            "github": actor.github,
            "profileImage": actor.profileImage
        },
        "object": {
            "type": "author",
            "id": object.url,
            "host": object.host,
            "displayName": object.displayName,
            "url": object.url,
            "github": object.github,
            "profileImage": object.profileImage
        }
    }

    # Set the URL to the actor's API Inbox URL

    # url = actor.url.replace("https://www.distribution.social", "http://127.0.0.1:8000") + "/inbox"

    url = actor.url + "/inbox"

    print("Sending!!!!!!")

    print(json, url)

    try:
        request = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers,json=json)

        print(request.status_code)
        print(request.text)
        print(request.json())
        print(request.reason)

        request.raise_for_status()

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
