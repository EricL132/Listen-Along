from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [

    path('getauth',AuthURL.as_view()),
    path('redirect',spotify_callback),
    path('checkauth',IsAuthenticated.as_view()),
    path('currentsong',CurrentSong.as_view()),
    path('play',PlaySong.as_view()),
    path('pause',PauseSong.as_view()),
    path('skip',SkipSong.as_view()),
    path('previous',PrevSong.as_view()),
    path('usersong',UserSong.as_view()),
]
