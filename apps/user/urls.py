from django.urls import path

from apps.user.views import Login, Register

urlpatterns = [
    path('login/', Login.as_view()),
    path('register/', Register.as_view())
]
