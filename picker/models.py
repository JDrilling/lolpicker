from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=20, unique=True)
    captain = models.ForeignKey(User)

    def __str__(self):
        return str(self.name)


class Game(models.Model):
    redTeam  = models.ForeignKey(Team, related_name="redTeam")
    blueTeam = models.ForeignKey(Team, related_name="blueTeam")

    currentPickBanRound = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{} vs {}".format(self.redTeam.name, self.blueTeam.name)


class Champion(models.Model):
    lolID = models.PositiveIntegerField()
    name = models.CharField(max_length=30)
    imageURL = models.TextField()

    def __str__(self):
        return str(self.name)


class PickBanRound(models.Model):
    RED_BAN   = "RB"
    RED_PICK  = "RP"
    BLUE_BAN  = "BB"
    BLUE_PICK = "BP"

    PICK_BAN_ROUND_TYPES = (
            (RED_BAN,   "Red Ban"),
            (RED_PICK,  "Red Pick"),
            (BLUE_BAN,  "Blue Ban"),
            (BLUE_PICK, "Blue Pick"),
        )

    game = models.ForeignKey(Game)

    roundNumber = models.PositiveIntegerField()
    roundType = models.CharField(max_length=2, choices=PICK_BAN_ROUND_TYPES)
    champion = models.ForeignKey(Champion, null=True, blank=True)

    def __str__(self):
        return "{} - Round {} ({})".format(self.game,
                                           self.roundNumber,
                                           self.get_roundType_display())

    class Meta:
        unique_together = ("game", "roundNumber")
