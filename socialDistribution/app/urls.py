from django.urls import path

from . import views

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('home', views.home, name='home'),
    path('login', views.signin, name='login'),
    path('logout', views.signout, name='logout'),
    path('<str:username>/following', views.following, name='following'),
    path('<str:username>/followers', views.followers, name='followers'),
    path('authors', views.authors, name='authors'),
    path('accounts/<str:username>', views.profile, name='profile'),
    path('<str:username>/true-friends', views.true_friends, name='true-friends'),
    path('<str:username>/received', views.received_requests, name='requests'),
    path('<str:username>/sent', views.sent_requests, name='sent_requests'),
    path('unfollow', views.followingTab, name='unfollow'),
    path('removefollower', views.followersTab, name='removefollower')
]
