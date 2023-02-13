from django.urls import path

from . import views

urlpatterns = [
    path('signup', views.signup, name='signup'),
    path('home', views.home, name='home'),
    path('login', views.signin, name='login'),
    path('logout', views.signout, name='logout'),
    path('<str:username>/following', views.following, name='following'),
    path('<str:username>/followers', views.followers, name='followers')
]