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

    started = models.BooleanField(default=False)
    currentRound = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{} vs {}".format(self.redTeam.name, self.blueTeam.name)


class Champion(models.Model):
    lolID = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=30)
    imageURL = models.TextField()
    staticAlias = models.TextField()

    def __str__(self):
        return str(self.name)


class PickBanRound(models.Model):
    RED = "R"
    BLUE = "B"
    PICK = "P"
    BAN = "B"

    SIDES = (
        (RED, "red"),
        (BLUE, "blue"),
    )

    ROUND_TYPES = (
        (PICK, "pick"),
        (BAN, "ban"),
    )

    game = models.ForeignKey(Game)

    roundNumber = models.PositiveIntegerField()
    roundType = models.CharField(max_length=1, choices=ROUND_TYPES)
    side = models.CharField(max_length=1, choices=SIDES)
    champion = models.ForeignKey(Champion, null=True, blank=True)

    duration = models.PositiveIntegerField()
    expiration = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{} - Round {} ({} {}): {}".format(self.game,
                                           self.roundNumber,
                                           self.get_side_display(),
                                           self.get_roundType_display(),
                                           self.champion)

    class Meta:
        unique_together = ("game", "roundNumber")
