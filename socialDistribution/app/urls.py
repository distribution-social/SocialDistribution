from django.urls import path

from . import views
from .API.views import *


urlpatterns = [
    path('', views.root, name='root'),
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
    path('delete-post/<uuid:post_id>/', views.delete_post, name='delete_post'),

    path('authors', views.authors, name='authors'),
    path('authors/<uuid:author_id>/inbox', views.inbox, name='inbox'),
    path('authors/<str:author_id>', views.profile, name='profile'),
    path('unfollow', views.unfollow, name='unfollow'),
    path('removefollower', views.removeFollower, name='removefollower'),
    path('authors/<uuid:author_id>', views.profile, name='profile'),
    path('<str:username>/true-friends', views.true_friends, name='true-friends'),
    path('authors/<uuid:author_id>/received', views.received_requests, name='requests'),
    path('authors/<uuid:author_id>/sent', views.sent_requests, name='sent_requests'),

    #API urls
    path('api/authors', AuthorListAPIView.as_view(), name='api-author-list'),
    path('api/authors/<uuid:author_id>', SingleAuthorAPIView.as_view(), name='api-single_author'),
    path('api/authors/<uuid:author_id>/followers', AuthorFollowersAPIView.as_view(), name='api-author-followers'),
    path('api/authors/<uuid:author_id>/followers/<uuid:follower_author_id>', FollowerAPIView.as_view(), name='api-followers'),
    path('api/authors/<uuid:author_id>/posts/<uuid:post_id>', PostDetailView.as_view(), name ='api-post-detail'),
    path('api/authors/<uuid:author_id>/posts', AuthorPostsView.as_view(), name ='api-author-post'),
    path('api/authors/<uuid:author_id>/liked', LikedView.as_view(), name ='api-author-liked'),
    path('api/authors/<uuid:author_id>/posts/<uuid:post_id>/comments', CommentsView.as_view(), name ='api-post-comments'),
    path('api/authors/<uuid:author_id>/posts/<uuid:post_id>/likes', LikesPostView.as_view(), name ='api-post-likes'),
    path('api/authors/<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>', LikesCommentView.as_view(), name ='api-post-comment'),
    path('api/authors/<uuid:author_id>/posts/<uuid:post_id>/comments/<uuid:comment_id>/likes', LikesCommentView.as_view(), name ='api-post-comment-likes'),

]
