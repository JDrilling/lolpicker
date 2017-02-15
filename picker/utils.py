import json
from django.db.models import F
from picker.models import PickBanRound as PBR, Game, Champion

RED_BAN = PBR.RED + PBR.BAN
RED_PICK = PBR.RED + PBR.PICK
BLUE_BAN = PBR.BLUE + PBR.BAN
BLUE_PICK = PBR.BLUE + PBR.PICK

TEN_BAN_SCHEME = [BLUE_BAN,  RED_BAN,   BLUE_BAN,
                  RED_BAN,   BLUE_BAN,  RED_BAN, # End Ban 1
                  BLUE_PICK, RED_PICK,  RED_PICK,
                  BLUE_PICK, BLUE_PICK, RED_PICK, # End Pick 1
                  RED_BAN,   BLUE_BAN,  RED_BAN,   BLUE_BAN, # End Ban 2
                  RED_PICK,  BLUE_PICK, BLUE_PICK, RED_PICK] # End Pick 2

def createNewTenBanGame(game):
    rounds = []

    for number, typ in enumerate(TEN_BAN_SCHEME):
        pbRound = PBR(game=game, roundNumber=number, roundType=typ[1], side=typ[0])

        rounds.append(pbRound)


    for r in rounds:
        r.save()

def validatePick(gameID, pickID, user):
    # User is logged in
    if not user.is_authenticated:
        return "Must log in to pick or ban!"

    # A champion was selected
    if pickID is None:
        return "No champion selected!"

    # The champion selection is valid
    champion = Champion.objects.get(lolID=pickID)
    if champion is None:
        return "Invalid champion ID."

    # There is game metadata
    game = Game.objects.get(id=gameID)

    pbrs = PBR.objects.filter(game=game)
    if len(pbrs) == 0:
        return "No game metadata."

    # Picks have started
    roundNumber = game.currentRound
    if roundNumber < 0:
        return "Picks and bans have not started for this game."

    # Picks have not finished
    if roundNumber >= len(pbrs):
        return "Picks and bans have already finished!"

    # Round exists
    currentRound = pbrs.get(roundNumber=roundNumber)
    if currentRound is None:
        return "Unexpected round..."

    # Check that the user is the captain of the picking team
    if currentRound.side == PBR.BLUE:
        if game.blueTeam.captain != user:
            return "You are not the captain of this team."
    elif currentRound.side == PBR.RED:
        if game.redTeam.captain != user:
            return "You are not the captain of this team."

    # Champion was not previously selected
    championsUsed = set([r.champion.lolID for r in pbrs if r.champion is not None])
    if pickID in championsUsed:
        return "Champion was already picked or banned."

    return None

def makePick(gameID, pickID):
    game = Game.objects.get(id=gameID)
    champion = Champion.objects.get(lolID=pickID)

    roundNumber = game.currentRound
    currentRound = PBR.objects.get(game=game, roundNumber=roundNumber)

    # Add Champion
    currentRound.champion = champion
    currentRound.save()

    # Start next round
    game.currentRound = F('currentRound') + 1
    game.save()

    return None

def getRoundsData(gameID):
    game = Game.objects.get(id=gameID)
    pbrs = PBR.objects.filter(game=game)

    roundData = {}
    for pbr in pbrs:
        data = { 'team': pbr.side,
                 'type': pbr.roundType,
                 'championID': pbr.champion.lolID if pbr.champion else None,
               }
        roundData[pbr.roundNumber] = data

    return roundData

def sendError(channel, error):
    response = { 'success': False,
                 'error': error,
               }
    channel.send({'text': json.dumps(response)})

def sendSuccess(channel, data):
    response = { 'success': True,
                 'data': data,
               }
    channel.send({'text': json.dumps(response)})
