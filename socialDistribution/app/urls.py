from django.urls import path

from . import views

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('home', views.home, name='home'),
    path('post', views.add_post, name='post-form'),
    path('author/search', views.author_search, name='author-search'),
    path('login', views.signin, name='login'),
    path('logout', views.signout, name='logout'),
    path('posts', views.posts, name='posts'),
    path('posts/<str:post_id>', views.post_detail, name='post_detail'),
    path('authors', views.authors, name='authors'),
    path('authors/<str:author_id>/inbox', views.inbox, name='inbox'),
    path('<str:username>/following', views.following, name='following'),
    path('<str:username>/followers', views.followers, name='followers'),
    path('<str:username>', views.profile, name='profile'),
    path('<str:username>/true-friends', views.true_friends, name='true-friends'),
    path('<str:username>/received', views.received_requests, name='requests'),
    path('<str:username>/sent', views.sent_requests, name='sent_requests'),



]
