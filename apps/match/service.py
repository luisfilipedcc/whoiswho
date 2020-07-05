from apps.game.service import GameService
from apps.match.exceptions import PlayerInvalidTurn, InvalidPlayerReference


class MatchService:

    def __init__(self, match):
        self.match = match

    def start(self, category, number_of_pieces):
        self.match.started = True
        game_service = GameService()
        game_service.start(category=category, number_of_pieces=number_of_pieces)
        self.match.game_state = game_service.game_state
        self.match.save()

    def join(self, player):
        if self.match.player1 == player:
            return
        self.match.waiting = False
        self.match.player2 = player
        self.match.save()

    def play(self, picks, is_player1, is_player2):
        last_play = self.match.game_state
        if last_play.side1_turn and is_player1 or last_play.side2_turn and is_player2:
            raise PlayerInvalidTurn()
        game_service = GameService()
        game_service.play(last_play, picks)
        self.match.game_state = game_service.game_state
        self.match.save()
        self._check_win(is_player1, is_player2)

    def leave(self, is_player1, is_player2):
        self.match.ended = True
        if self.match.player2:
            player1 = self.match.player1
            player2 = self.match.player2
            if is_player1:
                self._set_player_win(winner=player2, loser=player1)
            if is_player2:
                self._set_player_win(winner=player1, loser=player2)
        self.match.save()

    def get_restore_mask(self, is_player1, is_player2):
        if not is_player1 and not is_player2:
            raise InvalidPlayerReference
        game_state = self.match.game_state
        player_mask = game_state.side1_mask if is_player1 else game_state.side2_mask
        player_character = game_state.game.board.character1 if is_player1 else game_state.game.board.character2
        closed_characters = []
        for mask_item, piece in zip(player_mask.split(','), self.match.game_state.game.board.pieces.split(',')):
            if mask_item == "0" and int(piece) != player_character.id:
                closed_characters.append(int(piece))
        return closed_characters

    def _check_win(self, is_player1, is_player2):
        if self.match.game_state.last_play:
            player1 = self.match.player1
            player2 = self.match.player2
            if is_player1:
                if self.match.game_state.side1_won:
                    self.match.winner = player1
                    self._set_player_win(winner=player1, loser=player2)
                else:
                    self.match.winner = player2
                    self._set_player_win(winner=player2, loser=player1)
            if is_player2:
                if self.match.game_state.side2_won:
                    self.match.winner = player2
                    self._set_player_win(winner=player2, loser=player1)
                else:
                    self.match.winner = player1
                    self._set_player_win(winner=player1, loser=player2)
            self.match.ended = True
            self.match.save()

    @staticmethod
    def _set_player_win(winner, loser):
        winner.wins = winner.wins + 1
        loser.defeats = loser.defeats + 1
        winner.save()
        loser.save()

