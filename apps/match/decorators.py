from django.http import JsonResponse
from django.db.models import Q

from apps.match.models import Match


def active_turn(function):

    def _inner(self, request, *args, **kwargs):
        query = Q(player1=request.player)
        query.add(Q(player2=request.player), Q.OR)
        query.add(Q(pk=kwargs['match_id']), Q.AND)
        match = Match.objects.filter(query).first()
        if not match:
            return JsonResponse({"error": "Getting information of a match that does not exist or is not yours."})

        request.match = match
        request.is_player1 = match.player1 == request.player
        request.is_player2 = match.player2 == request.player

        return function(self, request, *args, **kwargs)

    return _inner


