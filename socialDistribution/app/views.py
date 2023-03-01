from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SignupForm, SigninForm, PostForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Author
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

from django.contrib.auth.models import User
from .helpers import is_valid_info


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            display_name = form.cleaned_data.get('display_name')
            try:
                first_name, last_name = display_name.split()
            except ValueError:
                first_name = display_name
                last_name = ""

            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            github = form.cleaned_data.get('github')
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')

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
                Author.objects.create(host="http://127.0.0.1:8000", displayName=display_name,
                                      github=f"https://github.com/{github}", profileImage=None, email=email, username=username)
            except Exception as e:
                messages.warning(request, e)
                return redirect(reverse('signup'))

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('home'))
            else:
                return redirect(reverse('signup'))
        else:
            return redirect(reverse('signup'))

    elif request.method == "GET":
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        else:
            context = {"title": "signup", "form": SignupForm()}
            return render(request, 'signup.html', context)


@require_http_methods(["GET"])
@login_required(login_url="/login")
def home(request):
    user = request.user
    author = Author.objects.get(username=user.username)
    context = {"user": user, "author": author}
    return render(request, 'home.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def add_post(request):
    user = Author.objects.get(username=request.user.username)

    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            if request.POST['visibility'] == 'PRIVATE':
                post = form.save(user=user, receiver_list = request.POST.getlist('receivers'))
            else:
                 post = form.save(user=user)
            # Do something with the saved data (e.g. redirect to a detail view)
            # return redirect('post_detail', pk=post.pk)

            return redirect(reverse('home'))
    elif request.method == "GET":
        context = {"title": "Create a Post", "form": PostForm()}
        return render(request, 'post.html', context)


@require_http_methods(["GET", "POST"])
def signin(request):
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('home'))
            else:
                messages.warning(request, "Invalid username or password")
                return redirect(reverse('login'))
    elif request.method == "GET":
        # No need to sign in again
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        else:
            context = {"title": "signin", "form": SigninForm()}
            return render(request, 'signin.html', context)


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def signout(request):
    if request.method == "GET":
        logout(request)
        return redirect(reverse('home'))


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def following(request, username):

    user = request.user

    if request.method == 'GET':
        author = Author.objects.get(username=username)

        context = {"follow": author.following.all().order_by('displayName'), "mode": "following",
                   "user": user, "author": author}
        return render(request, 'follow.html', context)

    elif request.method == 'POST':
        # Extract the username of the author to unfollow
        username_to_unfollow = request.POST.get("unfollow")

        # Get the author object to unfollow
        author_to_unfollow = Author.objects.get(username=username_to_unfollow)

        # Get the author object of the current user
        author = Author.objects.get(username=user)

        # Remove the author from the following of the current user
        author.following.remove(author_to_unfollow)

        return redirect(reverse("following", kwargs={'username': user.username}))


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def followers(request, username):
    user = request.user
    if request.method == 'GET':
        author = Author.objects.get(username=username)
        context = {"follow": author.followers.all().order_by('displayName'), "mode": "followers",
                   "user": user, "author": author}
        return render(request, 'follow.html', context)

    elif request.method == 'POST':
        # Extract the username of the author to remove from our followers
        username_to_remove = request.POST.get("remove")

        # Get the author object
        author_to_remove = Author.objects.get(username=username_to_remove)

        # Get our author object
        current_user_author = Author.objects.get(username=user.username)

        # We remove ourself to the author's followings list
        author_to_remove.following.remove(current_user_author)

        return redirect(reverse("followers", kwargs={'username': user.username}))


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def authors(request):
    if request.method == "GET":
        authors = list(Author.objects.exclude(
            username=request.user.username).order_by('displayName'))
        current_user_followings = Author.objects.get(
            username=request.user.username).following.all()
        current_user_sent_requests = Author.objects.get(
            username=request.user.username).sent_requests.all()

        ineligible_users = current_user_followings | current_user_sent_requests

        context = {"authors": authors, "ineligible_users": ineligible_users}
        return render(request, 'authors.html', context)

    elif request.method == "POST":
        # Get the username to follow
        username_to_follow = request.POST.get("follow")

        # Get the author object
        author_to_follow = Author.objects.get(username=username_to_follow)

        # Get our author object
        current_user_author = Author.objects.get(
            username=request.user.username)

        # Add the author object to our sent_request list (Need to send this to inbox in the future to get approval on the other end)
        current_user_author.sent_requests.add(author_to_follow)

        return redirect(reverse("authors"))


@login_required(login_url="/login")
@require_http_methods(["GET"])
def profile(request, username):
    if request.method == 'GET':
        return HttpResponse("Profile")


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
def received_requests(request, username):
    user = request.user

    if request.method == 'GET':

        follow_requests = Author.objects.get(
            username=request.user.username).follow_requests.all()

        context = {"requests": follow_requests, "mode": "received"}

        return render(request, 'requests.html', context)

    elif request.method == "POST":
        action, sender_username = request.POST.get("action").split("_")

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
            current_user_author.follow_requests.remove(sender_author)

        elif action == "decline":

            # Remove this follow request on the sender side
            sender_author.sent_requests.remove(current_user_author)

            # Remove this follow request on our side
            current_user_author.follow_requests.remove(sender_author)

        return redirect(reverse("requests", kwargs={'username': user.username}))


@login_required(login_url="/login")
@require_http_methods(["GET", "POST"])
def sent_requests(request, username):
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

        return redirect(reverse("requests", kwargs={'username': user.username}))
