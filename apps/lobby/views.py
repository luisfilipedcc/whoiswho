from django.http import JsonResponse
from django.views import View

from apps.user.decorators import logged_in
from apps.match.models import Match
from django.forms import model_to_dict


class Lobby(View):

    @logged_in
    def get(self, request):
        ongoing_matches = Match.objects.filter(ended=False, player2=None)
        return JsonResponse({"matches": [model_to_dict(match) for match in ongoing_matches]})
