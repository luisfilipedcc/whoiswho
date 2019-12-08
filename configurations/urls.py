"""configurations URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.match import urls as match_urls
from apps.user import urls as player_urls
from apps.lobby import urls as lobby_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('match/', include(match_urls)),
    path('player/', include(player_urls)),
    path('lobby/', include(lobby_urls))
]
