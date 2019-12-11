import json
import uuid

from django.forms import model_to_dict
from django.views import View

from apps.game.exceptions import GameNotEnoughCharacters
from apps.match.exceptions import PlayerInvalidTurn, InvalidPickSelection
from apps.user.decorators import logged_in
from apps.match.decorators import active_turn
from apps.match.models import Match
from django.http.response import JsonResponse

from apps.match.service import MatchService


class MatchStatus(View):

    @logged_in
    @active_turn
    def get(self, request, match_id):
        match_service = MatchService(request.match)
        game_state = match_service.match.game_state
        your_turn = not(request.is_player1 and game_state.side1_turn or request.is_player2 and game_state.side2_turn)
        opponent_pieces = game_state.missing_side2_pieces if request.is_player1 else game_state.missing_side1_pieces
        return JsonResponse({"ready": match_service.match.started,
                             "ended": match_service.match.ended,
                             "lost": game_state.side2_won if request.is_player1 else game_state.side1_won,
                             "your_turn": your_turn,
                             "opponent_pieces": opponent_pieces})


class MatchPlay(View):

    @logged_in
    @active_turn
    def post(self, request, match_id):
        if request.match.ended:
            return JsonResponse({"error": 1, "message": "Trying to play in a game that has already ended."})
        picks = json.loads(request.body).get('picks')
        if not picks:
            return JsonResponse({"error": 2, "message": "You should supply at least one pick every play."})
        match_service = MatchService(request.match)
        if not any([request.is_player1, request.is_player2]):
            return JsonResponse({"error": 3, "message": "It's no ones turn."})
        try:
            match_service.play(picks, request.is_player1, request.is_player2)
        except PlayerInvalidTurn:
            return JsonResponse({"error": 4, "message": "It's not this player's turn."})
        except InvalidPickSelection:
            return JsonResponse({"error": 5, "message": "A character picked was already selected."})
        game_state = match_service.match.game_state
        return JsonResponse({"won": game_state.side1_won if request.is_player2 else game_state.side2_won})


class MatchJoin(View):

    @logged_in
    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return JsonResponse({"error": 6, "message": "Match does not exist or is not yours."})
        if match.is_full:
            return JsonResponse({"joined": False})
        match.player2 = request.player
        match.save()
        return JsonResponse({"joined": True})


class MatchLeave(View):

    @logged_in
    @active_turn
    def post(self, request, match_id):
        try:
            match = Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return JsonResponse({"error": 6, "message": "Match does not exist or is not yours."})
        if not match.started:
            return JsonResponse({"error": 7, "message": "Trying to leave a match that has not started yet."})
        match_service = MatchService(match)
        match_service.leave(request.is_player1, request.is_player2)
        return JsonResponse({"left": True})


class MatchCreation(View):

    @logged_in
    def post(self, request):
        waiting_match = Match.objects.filter(player1=request.player, waiting=True).first()
        if waiting_match:
            return JsonResponse({"error": 8, "message": "You already have an ongoing match. Not creating a new one."})
        match_name = uuid.uuid4().hex[:6].upper()
        match = Match.objects.create(name=match_name, player1=request.player)
        match_service = MatchService(match)
        try:
            match_service.start(category="default", number_of_pieces=21)
        except GameNotEnoughCharacters:
            return JsonResponse({"error": 11, "message": "Creating a match with more characters than available."})
        return JsonResponse({"match_id": match.id})


class MatchCrud(View):

    @logged_in
    @active_turn
    def get(self, request, match_id):
        if request.match.waiting:
            return JsonResponse({"match": model_to_dict(request.match), "game": None, "board": None})
        board = model_to_dict(request.match.game_state.game.board)
        if request.is_player1:
            del board['character2']
        if request.is_player2:
            del board['character1']
        del board['pieces']
        board['characters'] = request.match.game_state.game.board.characters
        return JsonResponse({
            "match": model_to_dict(request.match),
            "game": model_to_dict(request.match.game_state.game),
            "board": board})

    @logged_in
    def delete(self, request, match_id):
        try:
            match = Match.objects.get(pk=match_id, player1=request.player)
        except Match.DoesNotExist:
            return JsonResponse({"error": 9, "message": "Deleting a match that is not yours or no longer exists."})
        if match.started:
            return JsonResponse({"error": 10, "message": "Cannot delete a match that has already started"})
        match.delete()
        return JsonResponse({"deleted": True})
