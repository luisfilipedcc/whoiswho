import json

from django.views import View
from django.http.response import JsonResponse

from django.contrib.auth import authenticate

from django.db import IntegrityError
from apps.user.models import Player


class Login(View):

    @staticmethod
    def post(request):
        request_data = json.loads(request.body)

        try:
            username = request_data['username']
            password = request_data['password']
        except KeyError:
            return JsonResponse({'error': 100, "message": "Please provide username/password"}, status=400)

        player = authenticate(request, username=username, password=password)
        if not player:
            return JsonResponse({'error': 101, "message": "Invalid credentials"}, status=400)

        return JsonResponse({'token': player.token})


class Register(View):

    @staticmethod
    def post(request):

        request_data = json.loads(request.body)

        try:
            username = request_data['username']
            email = request_data['email']
            password = request_data['password']
        except KeyError:
            return JsonResponse({'error': 102, "message": "Please provide an username, email and password"}, status=400)

        try:
            player = Player.objects.create_user(username=username, email=email, password=password)
        except IntegrityError:
            return JsonResponse({'error': 103, "message": "Email or username already registered"}, status=400)

        return JsonResponse({'player_id': player.id})
