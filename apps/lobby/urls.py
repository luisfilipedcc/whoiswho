from django.urls import path

from apps.lobby.views import Lobby

urlpatterns = [
    path('lobby/', Lobby.as_view()),
]
