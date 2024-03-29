from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.forms import model_to_dict


class Character(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)

    def __str__(self):
        return "Character {self.name} - id {self.id}".format(self=self)


class Board(models.Model):
    character1 = models.ForeignKey(
        Character, on_delete=models.DO_NOTHING, related_name="character1"
    )
    character2 = models.ForeignKey(
        Character, on_delete=models.DO_NOTHING, related_name="character2"
    )
    pieces = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=200, default=""
    )

    @property
    def character1_index(self):
        return self.pieces.split(',').index(str(self.character1.id))

    @property
    def character2_index(self):
        return self.pieces.split(',').index(str(self.character2.id))

    @property
    def characters(self):
        characters = Character.objects.filter(
            id__in=[int(p) for p in self.pieces.split(",")]
        ).order_by("id")
        return [model_to_dict(char) for char in characters]

    def __str__(self):
        return (
            "Board {self.id} : Char1 - {self.character1.name} : "
            "Char2 - {self.character2.name}"
        ).format(self=self)


class Game(models.Model):
    board = models.ForeignKey(Board, on_delete=models.DO_NOTHING)
    category = models.CharField(max_length=100)
    number_of_pieces = models.IntegerField()


class GameState(models.Model):
    game = models.ForeignKey(Game, on_delete=models.DO_NOTHING)
    side1_turn = models.BooleanField(default=True)
    side2_turn = models.BooleanField(default=False)
    side1_mask = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=200
    )
    side2_mask = models.CharField(
        validators=[validate_comma_separated_integer_list], max_length=200
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def last_play(self):
        return self.missing_side1_pieces == 1 or self.missing_side2_pieces == 1

    @property
    def missing_side1_pieces(self):
        return sum([int(x) for x in self.side1_mask.split(",")])

    @property
    def side1_won(self):
        return (
            self.missing_side1_pieces == 1
            and self.side1_mask.split(',').index("1") == self.game.board.character2_index
        )

    @property
    def missing_side2_pieces(self):
        return sum([int(x) for x in self.side2_mask.split(",")])

    @property
    def side2_won(self):
        return (
            self.missing_side2_pieces == 1
            and self.side2_mask.split(',').index("1") == self.game.board.character1_index
        )

    @property
    def open_characters(self):
        characters_ids = Character.objects.filter()
        return characters_ids

    def __str__(self):
        return "GameState {self.id} : Board {self.board.id}".format(self=self)
