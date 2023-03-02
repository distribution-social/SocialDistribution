from django.urls import path

from . import views
from .API.views import *


urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('home', views.home, name='home'),
    path('post', views.add_post, name='post-form'),
    path('author/search', views.author_search, name='author-search'),
    path('login', views.signin, name='login'),
    path('logout', views.signout, name='logout'),
    path('posts', views.posts, name='posts'),
    path('posts/<str:post_id>', views.post_detail, name='post_detail'),
    path('posts/<str:post_id>/comment', views.add_comment, name='comment-form'),
    path('posts/<str:post_id>/like', views.add_like_post, name='add_like_post'),
    path('posts/<str:post_id>/comments/<str:comment_id>/like', views.add_like_comment, name='add_like_comment'),


    path('authors', views.authors, name='authors'),
    path('authors/<str:username>/inbox', views.inbox, name='inbox'),
    path('<str:username>/following', views.following, name='following'),
    path('<str:username>/followers', views.followers, name='followers'),
    path('<str:username>', views.profile, name='profile'),
    path('<str:username>/true-friends', views.true_friends, name='true-friends'),
    path('<str:username>/received', views.received_requests, name='requests'),
    path('<str:username>/sent', views.sent_requests, name='sent_requests'),

    #API urls
    path('api/authors/', AuthorListAPIView.as_view(), name='api-author-list'),
    path('api/authors/<uuid:author_id>/', SingleAuthorAPIView.as_view(), name='api-single_author'),
    path('api/authors/<uuid:author_id>/followers/', AuthorFollowersAPIView.as_view(), name='api-author-followers'),
    path('api/authors/<uuid:author_id>/followers/<uuid:follower_author_id>/', FollowerAPIView.as_view(), name='api-followers'),
    path('api/authors/<uuid:author_id>/posts/<uuid:post_id>/', PostDetailView.as_view(), name ='api-post-detail'),
    path('api/authors/<uuid:author_id>/posts/', AuthorPostsView.as_view(), name ='api-author-post'),
]
