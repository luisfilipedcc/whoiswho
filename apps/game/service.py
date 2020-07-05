import random

from apps.game.exceptions import GameNotEnoughCharacters
from apps.game.models import Character, Board, Game, GameState
from apps.match.exceptions import InvalidPickSelection


class GameService:

    game_state = None

    def __init__(self):
        pass

    def play(self, last_game_state, picks):

        if last_game_state.side1_turn:
            new_side1_mask = last_game_state.side1_mask
            new_side2_mask = self._transform_mask_by_picks(last_game_state.side2_mask, picks)
        else:
            new_side1_mask = self._transform_mask_by_picks(last_game_state.side1_mask, picks)
            new_side2_mask = last_game_state.side2_mask

        self.game_state = GameState.objects.create(game=last_game_state.game,
                                                   side1_turn=not last_game_state.side1_turn,
                                                   side2_turn=not last_game_state.side2_turn,
                                                   side1_mask=new_side1_mask,
                                                   side2_mask=new_side2_mask)

    def start(self, category, number_of_pieces):
        if Character.objects.filter(category=category).count() < number_of_pieces:
            raise GameNotEnoughCharacters()

        player_characters = self._random_characters(2, category)
        pieces_characters = self._random_characters(number_of_pieces, category, player_characters)

        board = Board.objects.create(character1=player_characters[0],
                                     character2=player_characters[1],
                                     pieces=','.join([str(char.id) for char in pieces_characters]))

        game = Game.objects.create(board=board, category=category, number_of_pieces=number_of_pieces)

        side1_mask = ','.join(['1' if i != board.character1_index else '0' for i in range(number_of_pieces)])
        side2_mask = ','.join(['1' if i != board.character2_index else '0' for i in range(number_of_pieces)])

        self.game_state = GameState.objects.create(game=game,
                                                   side1_mask=side1_mask,
                                                   side2_mask=side2_mask)

    @staticmethod
    def _transform_mask_by_picks(mask, picks):
        mask_list = [int(x) for x in mask.split(',')]
        for pick_index in picks:
            if mask_list[pick_index] == 0:
                raise InvalidPickSelection()
            mask_list[pick_index] = 0
        return ','.join([str(x) for x in mask_list])

    @staticmethod
    def _random_characters(count, category, required_characters=None):
        required_characters_count = 0
        characters = Character.objects.filter(category=category).order_by('id')
        if required_characters is not None:
            required_characters_count = len(required_characters)
            characters = characters.exclude(pk__in=[rc.id for rc in required_characters])
        random_characters = [characters[pick] for pick in
                             random.sample([i for i in range(characters.count())], count - required_characters_count)]
        if required_characters is not None:
            random_characters.extend(required_characters)
        random_characters.sort(key=lambda x: x.id)
        return random_characters
