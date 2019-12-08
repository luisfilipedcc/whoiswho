from django.db import models
from apps.user.models import Player
from apps.game.models import GameState


class Match(models.Model):
    name = models.CharField(max_length=200)
    player1 = models.ForeignKey(Player, on_delete=models.DO_NOTHING, related_name="player1")
    player2 = models.ForeignKey(Player, on_delete=models.DO_NOTHING, related_name="player2", null=True)
    waiting = models.BooleanField(default=True)
    started = models.BooleanField(default=False)
    ended = models.BooleanField(default=False)
    game_state = models.ForeignKey(GameState, on_delete=models.DO_NOTHING, null=True)

    @property
    def is_full(self):
        return self.player2 is not None
