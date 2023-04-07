from django.shortcuts import render, redirect
from django.http import *
from app.API.helpers import get_full_uri

from app.API.paginators import CustomPaginator
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

from django.contrib.auth.models import User
from .helpers import *
from django.db.models import Q
from django.conf import settings

import urllib.parse
from .API.serializers import AuthorSerializer, CommentSerializer, PostSerializer

import feedparser

from django.http import JsonResponse

import feedparser

from django.http import JsonResponse


class HttpResponseUnauthorized(HttpResponse):
    status_code = 401


@require_http_methods(["GET"])
def root(request):
    # redirects to home page
    return redirect(reverse('explore'))


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "POST":

        form_inputs = request.POST
        display_name = form_inputs.get('display_name')
        username = form_inputs.get('username')
        email = form_inputs.get('email')
        github = form_inputs.get('github')
        password = form_inputs.get('password')
        confirm_password = form_inputs.get('confirm_password')

        if display_name and username and email and github and password and confirm_password:

            try:
                first_name, last_name = display_name.split()
            except ValueError:
                first_name = display_name
                last_name = ""

            if not is_valid_info(request, username, email, github, password, confirm_password):
                return redirect(reverse('signup'))

            try:
                u = User.objects.create_user(
                    username, email, password, first_name=first_name, last_name=last_name)
            except Exception as e:
                messages.warning(request, e)
                return redirect(reverse('signup'))
            else:
                u.save()

            try:
                Author.objects.create(displayName=display_name,
                                      github=f"https://github.com/{github}", profileImage=None, email=email, username=username, confirmed=False)
            except Exception as e:
                messages.warning(request, e)
                return redirect(reverse('signup'))

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('home'))
                else:
                    messages.warning(
                        request, "Please contact the admin to be confirmed and be able to login")
                    return redirect(reverse('login'))
            else:
                messages.warning(
                    request, "Please contact the admin to be confirmed and be able to login")
                return redirect(reverse('signup'))
        else:
            return redirect(reverse('signup'))

    elif request.method == "GET":
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        else:
            return render(request, 'signup.html')


@require_http_methods(["GET"])
@login_required(login_url="/login")
def home(request):
    context = {"comment_form": CommentForm()}
    return render(request, 'home_stream.html', context)


@require_http_methods(["GET"])
def explore(request):
    context = {"comment_form": CommentForm()}
    return render(request, 'explore_stream.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def author_search(request):

    if request.POST.get('action') == 'author-search':
        search_term = str(request.POST.get('query_term'))

        if search_term:
            search_term = Author.objects.filter(
                username__icontains=search_term, host__contains="distribution.social" )[:5]

            data = serializers.serialize('json', list(
                search_term), fields=('id', 'username'))

            return JsonResponse({'search_term': data})


def delete_post(request, post_id):
    post = Post.objects.get(uuid=post_id)

    if request.method == 'POST':
        # Verify that the user is allowed to delete the post
        if post.made_by.username != request.user.username:
            return JsonResponse({'success': False, 'message': 'You are not authorized to delete this post.'})

        # Delete the post
        post.delete()

        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def add_post(request):
    user = Author.objects.get(username=request.user.username)

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():

            post = form.save(user=user)

            # if request.POST['visibility'] == 'PRIVATE':
            for receiver_id in request.POST.getlist('receivers'):
                author = Author.objects.get(id=receiver_id)
                foreign_node = get_foreign_API_node(author.host)
                if foreign_node:
                    auth_token = ''
                    if foreign_node.username:
                        auth_token = foreign_node.getToken()

                    serializer = PostSerializer(post, context={'request':request,'kwargs':{'author_id':user.id,'post_id':post.uuid}})
                    data = serializer.data

                    comments = post.comments.all().order_by('-published')
                    # paginator = CustomPaginator()
                    # commentResultPage = paginator.paginate_queryset(comments, request)
                    context = {'request':request,'kwargs':{'author_id':user.id,'post_id':data['id'].split("/")[-1]}}
                    comment_serializer = CommentSerializer(comments, many=True, context=context)

                    response = {
                        "type": "comments",
                        "post": get_full_uri(request,'api-post-detail',context['kwargs']),
                        "id": get_full_uri(request,'api-post-comments',context['kwargs']),
                        "comments": comment_serializer.data,
                    }

                    data["commentSrc"] = response
                    data['count'] = len(comments)

                    url = f"{author.url}/inbox"
                    headers = {
                        "Authorization": f"Basic {auth_token}",
                        "Content-Type": 'application/json; charset=utf-8',

                    }

                    response = requests.post(url, data=json.dumps(data), headers=headers)
                    response.raise_for_status()

                else:
                    raise("Error finding foreign Node")

            return redirect(reverse('node-post-detail', kwargs={'node': 'Local','author_id': user.id,'post_id': post.uuid}))
    elif request.method == "GET":
        context = {"title": "Create a Post", "form": PostForm(
            author=user), "action": "PUBLISH"}
        return render(request, 'post.html', context)


@require_http_methods(["GET", "POST"])
def signin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if username and password:
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect(reverse('home'))
                else:
                    messages.warning(
                        request, "Your account is not confirmed. Please contact the admin to get their approval.")
                    return redirect(reverse('login'))
            else:
                messages.warning(
                    request, "Invalid username, invalid password, or unconfirmed user.")
                return redirect(reverse('login'))

        # Username and/or password is missing
        else:
            messages.warning(
                request, "Invalid username, invalid password, or unconfirmed user.")
            return redirect(reverse('login'))

    elif request.method == "GET":
        # No need to sign in again
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        else:
            context = {"title": "signin", "form": SigninForm()}
            return render(request, 'signin.html', context)


@login_required(login_url="/login")
@require_http_methods(["POST"])
def signout(request):
    if request.method == "POST":
        logout(request)
        return redirect(reverse('explore'))


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def authors(request):
    if request.method == "GET":
        authors = list(Author.objects.exclude(Q(
            username=request.user.username) | Q(confirmed=False)).order_by('displayName'))
        current_user_followings = Author.objects.get(
            username=request.user.username).following.all()
        current_user_sent_requests = Author.objects.get(
            username=request.user.username).sent_requests.all()

        ineligible_users = current_user_followings | current_user_sent_requests

        context = {"authors": authors, "ineligible_users": ineligible_users}
        return render(request, 'authors.html', context)

    elif request.method == "POST":
        # Get the username to follow
        id_to_follow = request.POST.get("follow")

        # Get the author object
        author_to_follow = Author.objects.get(id=id_to_follow)

        # Get our author object
        current_user_author = Author.objects.get(
            username=request.user.username)

        # Add the author object to our sent_request list (Need to send this to inbox in the future to get approval on the other end)
        current_user_author.sent_requests.add(author_to_follow)
        add_to_inbox(current_user_author, author_to_follow,
                     Activity.FOLLOW, current_user_author)

        return redirect(reverse("authors"))


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def add_to_following(request):
    if request.method == "POST":
        body_dict = json.loads(request.body)
        id_to_add_to_following = body_dict.get('author_id')

        # ForeignUserObject
        foreign_user_object = body_dict.get('foreign_user_object')

        try:
            # Get the foreign author's object
            author_object_to_add_to_following = Author.objects.get(
                id=id_to_add_to_following)
        except Author.DoesNotExist:
            random_uuid = uuid.uuid4()
            author_to_follow = Author(id=random_uuid, host=foreign_user_object["host"], url=foreign_user_object["url"], displayName=foreign_user_object["displayName"],
                                      github=foreign_user_object["github"], profileImage=foreign_user_object["profileImage"], username=str(random_uuid), confirmed=True)

            author_to_follow.save()

        # Get our author object
        current_user_author = Author.objects.get(
            username=request.user.username)

        # Add the object as one of our current author's following
        try:
            current_user_author.following.get(id=id_to_add_to_following)
        except:
            current_user_author.following.add(author_object_to_add_to_following)

        try:
            # Remove from sent_requests
            current_user_author.sent_requests.remove(author_object_to_add_to_following)
        except:
            pass

        return HttpResponse("Success")
    else:
        return HttpResponse("Method Not Allowed")


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def add_to_sent_request(request):
    if request.method == "POST":
        print("********************")
        body_dict = json.loads(request.body)
        id_to_follow = body_dict.get('author_id')

        # ForeignUserObject
        foreign_user_object = body_dict.get('foreign_user_object')

        try:
            # Get the foreign author's object
            author_to_follow = Author.objects.get(id=id_to_follow)
        except Author.DoesNotExist:
            random_uuid = uuid.uuid4()
            author_to_follow = Author(id=random_uuid, host=foreign_user_object["host"], url=foreign_user_object["url"], displayName=foreign_user_object["displayName"],
                                      github=foreign_user_object["github"], profileImage=foreign_user_object["profileImage"], username=str(random_uuid), confirmed=True)

            author_to_follow.save()

        # Get our author object
        current_user_author = Author.objects.get(
            username=request.user.username)

        # Add the author object to our sent_request list (Need to send this to inbox in the future to get approval on the other end)
        current_user_author.sent_requests.add(author_to_follow)

        return HttpResponse("Success")
    else:
        return HttpResponse("Method Not Allowed")


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def profile(request, server_name, author_id):
    # import pdb; pdb.set_trace()
    user = request.user

    userAuthor = Author.objects.get(username=request.user.username)
    if request.method == 'GET':

        context = {"user": userAuthor, "server_name": server_name,
                   "author_id": author_id, "user_id": str(userAuthor.id)}
        if str(userAuthor.id) == author_id:
            requests = Author.objects.get(
                id=userAuthor.id).follow_requests.all()
            context.update({"requests": requests, "mode": "received",
                           "edit_profile_form": EditProfileForm(instance=userAuthor)})
        else:
            try:
                userFollows = userAuthor.following.get(id=author_id)
                context.update({"user_is_following": "True"})
            except:
                context.update({"user_is_following": "False"})
        local_node = ForeignAPINodes.objects.get(nickname="Local")
        try:
            node = ForeignAPINodes.objects.get(nickname=server_name)
        except:
            node = local_node
        headers = json.dumps(
            {'Authorization': f"Basic {node.getToken()}", 'Content-Type': 'application/json'})
        context.update({"auth_headers": headers, "local_server_host": request.get_host(
        ), "server_url": node.base_url})

        headers = json.dumps(
            {'Authorization': f"Basic {local_node.getToken()}", 'Content-Type': 'application/json'})
        context.update({"local_auth_headers": headers})

        context.update({"nicknameTable": getNicknameTable()})
        context.update({"tokenTable": getTokenTable()})
    
        id_to_follow = author_id

        # Get the author object
        try:
            author_to_follow = Author.objects.get(id=id_to_follow)

            # Get our author object
            current_user_author = Author.objects.get(
                username=request.user.username)

            # Add the author object to our sent_request list (Need to send this to inbox in the future to get approval on the other end)
            if current_user_author.sent_requests.filter(id=author_to_follow.id).exists():
                context.update({"user_pending_following": "True"})
            else:
                context.update({"user_pending_following": "False"})
        except:
            context.update({"user_pending_following": "False"})

        context.update({'foreign_node_token': node.getToken()})
        context.update({'local_node_token': local_node.getToken()})

        return render(request, 'profile.html', context)

    elif request.method == "POST":
        author_for_action = Author.objects.get(id=author_id)
        foreignNode = getApiNodeWrapper(userAuthor.host)
        if author_for_action in userAuthor.following.all():
            # Remove the author from the following of the current user
            userAuthor.following.remove(author_for_action)
        else:
            # Add the author object to our sent_request list (Need to send this to inbox in the future to get approval on the other end)
            userAuthor.sent_requests.add(author_for_action)

        return redirect(reverse("profile", kwargs={"server_name": foreignNode.nickname, "author_id": userAuthor.id}))


def getNicknameTable():
    nodes = ForeignAPINodes.objects.all()
    table = {}
    for node in nodes:
        parsedHost = urllib.parse.urlparse(node.base_url)
        table.update({str(parsedHost.hostname): node.nickname})
    return json.dumps(table)

def getTokenTable():
    nodes = ForeignAPINodes.objects.all()
    table = {}
    for node in nodes:
        parsedHost = urllib.parse.urlparse(node.base_url)
        table.update({str(parsedHost.hostname): node.getToken()})
    return json.dumps(table)

def getServerNickname(request, url):
    parsedHost = urllib.parse.urlparse(url)
    node = ForeignAPINodes.objects.get(
        base_url__contains="//"+parsedHost.hostname)
    return node.nickname


def getApiNodeWrapper(host):
    parsedHost = urllib.parse.urlparse(host)
    try:
        node = ForeignAPINodes.objects.get(base_url__contains="//"+parsedHost.hostname)
    except:
        return ForeignAPINodes.objects.get(base_url__contains=settings.HOST)
    return node


def getAuthHeadersJson(author_host):
    node = getApiNodeWrapper(author_host)
    headers = {}
    if node.username:
        headers = {'Authorization': f"Basic {node.getToken()}",
                   'Content-Type': 'application/json'}
    return json.dumps(headers)


def get_posts_visible_to_user(userAuthor, author, friends):
    if userAuthor.id == author.id:
        return Post.objects.filter(made_by=author).order_by('-date_published')
    public = Post.objects.filter(made_by=author, visibility="PUBLIC")
    # private = Post.objects.filter(made_by=author, receivers__contains=user)
    if userAuthor in friends:
        friends = Post.objects.filter(made_by=author, visibility="FRIENDS")
        # posts = (private | public | friends).distinct()
        posts = (public | friends).distinct()
    else:
        # posts = (private | public).distinct()
        posts = public

    return posts.order_by('-date_published')


@login_required(login_url="/login")
@require_http_methods(["POST"])
def unfollow(request):
    user = request.user
    # Extract the username of the author to unfollow
    id_to_unfollow = request.POST.get("unfollow")
    # Get the author object to unfollow
    author_to_unfollow = Author.objects.get(id=id_to_unfollow)
    # Get the author object of the current user
    user_author = Author.objects.get(username=user)
    # Remove the author from the following of the current user
    user_author.following.remove(author_to_unfollow)

    return redirect(reverse("profile", kwargs={"author_id": user_author.id}))


@login_required(login_url="/login")
@require_http_methods(["POST"])
def removeFollower(request):
    user = request.user
    # Extract the username of the author to remove from our followers
    id_to_remove = request.POST.get("removefollower")
    # Get the author object
    author_to_remove = Author.objects.get(id=id_to_remove)
    # Get our author object
    user_author = Author.objects.get(username=user.username)
    # We remove ourself to the author's followings list
    author_to_remove.following.remove(user_author)

    return redirect(reverse("profile", kwargs={"author_id": user_author.id}))


@login_required(login_url="/login")
@require_http_methods(["GET"])
def true_friends(request, username):
    if request.method == 'GET':

        author = Author.objects.get(username=username)

        followings = set(author.following.all())

        followers = set(author.followers.all())

        true_friends = list(followings & followers)

        context = {"friends": true_friends, "author": author}

        return render(request, 'true-friends.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def received_requests(request, author_id):
    # import pdb; pdb.set_trace()
    user = request.user

    author = Author.objects.get(id=author_id)
    node = ForeignAPINodes.objects.get(base_url=author.host)

    if request.method == 'GET':

        follow_requests = Author.objects.get(
            username=request.user.username).follow_requests.all()

        context = {"requests": follow_requests, "mode": "received"}

        return render(request, 'requests.html', context)

    elif request.method == "POST":
        response = ""
        inbox = None
        profile = None
        request_action = request.POST.get("action").split("_")
        if len(request_action) < 2:
            return HttpResponseBadRequest("Not enough action parameters")
        action = request_action[0]
        sender_username = request_action[1]
        if len(request_action) > 2:
            if request_action[2] == "inbox":
                inbox = request_action[2]
            elif request_action[2] == "profile":
                profile = request_action[2]
        sender_author = Author.objects.get(username=sender_username)

        # Get our author object
        current_user_author = Author.objects.get(
            username=request.user.username)

        if action == "accept":
            # Add ourself to the sender author's following
            sender_author.following.add(current_user_author)

            # Remove this follow request on the sender side
            sender_author.sent_requests.remove(current_user_author)

            # Remove this follow request on our side
            # current_user_author.follow_requests.remove(sender_author)
            response = "Accepted"

            # Send a type == "accept" to the user's node
            send_post_request("accept", sender_author, current_user_author)

        elif action == "decline":

            # Remove this follow request on the sender side
            sender_author.sent_requests.remove(current_user_author)

            # Remove this follow request on our side
            current_user_author.follow_requests.remove(sender_author)
            response = "Declined"

        if inbox:
            return redirect(reverse("inbox", kwargs={'author_id': convert_username_to_id(user.username)}))
        elif profile:
            return redirect(reverse("profile", kwargs={'server_name': "Local", 'author_id': convert_username_to_id(user.username)}))
        else:
            return redirect(reverse("requests", kwargs={'server_name': "Local", 'author_id': convert_username_to_id(user.username)}))


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def sent_requests(request, author_id):
    user = request.user

    if request.method == 'GET':

        sent_requests = Author.objects.get(
            username=request.user.username).sent_requests.all()

        context = {"requests": sent_requests, "mode": "sent"}

        return render(request, 'requests.html', context)

    elif request.method == "POST":
        action, receiver_username = request.POST.get("action").split("_")

        receiver_author = Author.objects.get(username=receiver_username)

        # Get our author object
        current_user_author = Author.objects.get(
            username=request.user.username)

        if action == "cancel":
            # Remove it from our sent requests
            current_user_author.sent_requests.remove(receiver_author)

            # Remove it from the receiver side
            receiver_author.follow_requests.remove(current_user_author)

        return redirect(reverse("profile", kwargs={'server_name': "Local", 'author_id': convert_username_to_id(user.username)}))


# @login_required(login_url="/login")
# @require_http_methods(["GET"])
# def posts(request):
#     posts = Post.objects.all().order_by('-date_published')

#     context = {"posts": posts, "comment_form": CommentForm()}

#     return render(request, 'posts_stream.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET"])
def post_detail(request, post_id):

    # TODO: Check if post is on different host, if yes, then poll info from that particular hosts endpoint, and then pass that data on.
    post = Post.objects.get(uuid=post_id)
    context = {"request": request, "post": str(
        post.uuid), "comment_form": CommentForm()}

    return render(request, 'post_detail.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def post_edit(request, post_id):
    post = Post.objects.get(uuid=post_id)
    user = Author.objects.get(username=request.user.username)
    if request.method == "POST":
        if post.made_by.username != request.user.username:
            return JsonResponse({'success': False, 'message': 'You are not authorized to delete this post.'})
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            # Save the form data to the database
            if request.POST['visibility'] == 'PRIVATE':
                print("saving")
                post = form.save(
                    user=user, receiver_list=request.POST.getlist('receivers'))
                print("saved")
            else:
                print("saving")
                post = form.save(user=user)
                print("saved")
            # Do something with the saved data (e.g. redirect to a detail view)
            # return redirect('post_detail', pk=post.pk)

            return redirect(reverse('home'))
        if form.is_valid():
            print(form.errors)
            return HttpResponseBadRequest("Invalid form")

    elif request.method == "GET":
        context = {"title": "Edit Your Post", "form": PostForm(
            instance=post), "action": "SAVE", "post": post}
        if post.made_by.username != request.user.username:
            return JsonResponse({'success': False, 'message': 'You are not authorized to delete this post.'})
        return render(request, 'post_edit.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def inbox(request, author_id):

    # Requested author
    requested_author = Author.objects.get(id=author_id)

    # Current user's author
    author = Author.objects.get(username=request.user.username)

    if requested_author != author:
        return HttpResponseUnauthorized()
    context = {"type": "inbox"}

    if request.method == "GET":
        all = author.my_inbox.all().order_by("-date")
        likes = all.filter(object__type="like")
        comments = all.filter(object__type="comment")
        posts = all.filter(object__type="post")
        requests = all.filter(object__type="follow")
        context.update({"items": all, "likes": likes,
                       "comments": comments, "posts": posts, "requests": requests})

    elif request.method == "POST" and request.POST.get("action") == "clear_inbox":
        author.my_inbox.all().delete()

    return render(request, 'inbox.html', context)


@login_required(login_url="/login")
@require_http_methods(["POST"])
def add_comment(request, post_id):
    user = Author.objects.get(username=request.user.username)
    post = Post.objects.get(uuid=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(user=user, post=post)
            add_to_inbox(user, post.made_by, Activity.COMMENT, post)

            # Do something with the saved data (e.g. redirect to a detail view)
            # return redirect('post_detail', pk=post.pk)

            return redirect(reverse('post_detail', kwargs={'post_id': post.uuid}))


@login_required(login_url="/login")
@require_http_methods(["POST"])
def edit_profile(request, author_id):
    user = Author.objects.get(username=request.user.username)
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect(reverse('profile', kwargs={'server_name': 'Local','author_id': author_id}))
        else:
            print(form.errors)
            return HttpResponseBadRequest("Invalid form")


@login_required(login_url="/login")
@require_http_methods(["POST"])
def add_like_post(request, post_id):
    user = Author.objects.get(username=request.user.username)
    post = Post.objects.get(uuid=post_id)
    response = HttpResponse()

    if request.method == "POST":
        if post.made_by == user:
            response.content = "Can't like your own post."
            return response
        found = post.likes.filter(author=user)
        if not found:
            post.likes.create(type=Like.POST, author=user,
                              summary=f'{user.displayName} liked your post.')
            add_to_inbox(user, post.made_by, Activity.LIKE, post)
            response.content = "Liked"
        else:
            response.content = "Already liked this post."

    return response


@login_required(login_url="/login")
@require_http_methods(["GET"])
def get_is_pending(request, author_id):
    
    current_author = Author.objects.get(username=request.user.username)
    try:
        author_to_search = Author.objects.get(id=author_id)
    except:
        return JsonResponse({'is_pending': False})
    else:
        sent_requests = current_author.sent_requests.all()

        if author_to_search in sent_requests:
            return JsonResponse({'is_pending': True})
        else:
            return JsonResponse({'is_pending': False})



@login_required(login_url="/login")
@require_http_methods(["POST"])
def add_like_comment(request, post_id, comment_id):
    user = Author.objects.get(username=request.user.username)
    post = Post.objects.get(uuid=post_id)
    comment = Comment.objects.get(uuid=comment_id)
    response = HttpResponse()

    if request.method == "POST":
        if comment.author == user:
            response.content = "Can't like your own comment."
            return response
        found = comment.likes.filter(author=user)
        if not found:
            comment.likes.create(type=Like.COMMENT, author=user,
                                 summary=f'{user.displayName} liked your comment.')
            add_to_inbox(user, comment.author, Activity.LIKE, comment)
            response.content = "Liked"
        else:
            response.content = "Already liked this comment."

    return response


# @login_required(login_url="/login")
@require_http_methods(["GET"])
def github_activity(request, username):
    """
    Returns a JSON string of a user's GitHub activity
    """

    feed = feedparser.parse(f"https://github.com/{username}.atom")

    activities = []

    entries = feed.entries

    for entry in entries:
        entry_dict = {
            "id": entry.id,
            "published": entry.published,
            "updated": entry.updated,
            "title": entry.title,
            "link": entry.link,
            "author": entry.author,
            "authors": entry.authors,
            "media": entry.media_thumbnail,
            "content": entry.content,
            "summary": entry.summary
        }

        activities.append(entry_dict)

    return JsonResponse(activities, safe=False)
