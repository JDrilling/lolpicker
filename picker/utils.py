import json
import time
import threading
import sched
from channels import Group
from django.db.transaction import atomic
from picker.models import PickBanRound as PBR, Game, Champion
from django.core.exceptions import ObjectDoesNotExist

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

BAN_DURATION = 30
PICK_DURATION = 30

@atomic
def createNewTenBanGame(redTeam, blueTeam):
    game = Game(redTeam=redTeam, blueTeam=blueTeam, started=False)
    game.save()

    rounds = []

    for number, typ in enumerate(TEN_BAN_SCHEME):
        duration = 0
        if typ[1] == PBR.PICK:
            duration = PICK_DURATION
        else:
            duration = BAN_DURATION

        pbRound = PBR(game=game, roundNumber=number, roundType=typ[1], side=typ[0], duration=duration)

        rounds.append(pbRound)

    for r in rounds:
        r.save()

    return game


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
    if not game.started:
        return "Picks and bans have not started for this game."

    roundNumber = game.currentRound
    # Picks have not finished
    if roundNumber >= len(pbrs):
        return "Picks and bans have already finished!"

    # Round exists
    currentRound = pbrs.get(roundNumber=roundNumber)
    if currentRound is None:
        return "Unexpected round..."

    # Round is not over
    curTime = int(time.time())
    if curTime > currentRound.expiration:
        return "You can no longer pick for this round!"

    # Check that the user is the captain of the picking team
    if currentRound.side == PBR.BLUE:
        if game.blueTeam.captain != user:
            return "You are not the captain of this team."
    elif currentRound.side == PBR.RED:
        if game.redTeam.captain != user:
            return "You are not the captain of this team."

    # Champion was not previously selected
    championsUsed = {r.champion.lolID for r in pbrs if r.champion is not None}
    if int(pickID) in championsUsed:
        print('here')
        return "Champion was already picked or banned."

    return None

def startRound(game, rnd):
    curTime = round(time.time())
    rnd.expiration = rnd.duration + curTime
    rnd.save()

    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enterabs(rnd.expiration, 1, timeOutRound, (game.id, rnd.roundNumber))
    threading.Thread(target=scheduler.run, daemon=True).start()


def startPicking(gameID):
    # Signal the game has started
    game = Game.objects.get(id=gameID)
    game.started = True
    game.currentRound = 0
    game.save()

    # Signal the round has started
    firstRound = PBR.objects.get(game=game, roundNumber=0)
    startRound(game, firstRound)

def makePick(gameID, pickID):
    game = Game.objects.get(id=gameID)
    champion = Champion.objects.get(lolID=pickID)

    roundNumber = game.currentRound
    currentRound = PBR.objects.get(game=game, roundNumber=roundNumber)

    # Add Champion
    currentRound.champion = champion
    currentRound.save()

    roundNumber = roundNumber + 1

    # Start next round
    game.currentRound = roundNumber
    game.save()

    try:
        nextRound = PBR.objects.get(game=game, roundNumber=roundNumber)
        startRound(game, nextRound)
    except ObjectDoesNotExist:
        return None

    return None

def getRoundsData(game):
    pbrs = PBR.objects.filter(game=game)

    roundData = {}
    for pbr in pbrs:
        data = { 'team': pbr.side,
                 'type': pbr.roundType,
                 'championID': pbr.champion.lolID if pbr.champion else None,
               }
        roundData[pbr.roundNumber] = data

    return roundData

def getGameData(gameID):
    game = Game.objects.get(id=gameID)
    roundsData = getRoundsData(game)
    currentRoundNumber = game.currentRound
    expiration = 0
    duration = 0

    try:
        currentRound = PBR.objects.get(game=game, roundNumber=currentRoundNumber)
        expiration = currentRound.expiration
        curTime = round(time.time())
        duration = expiration - curTime
    except ObjectDoesNotExist:
        expiration = time.time()

    gameData = {
        'currentRound': currentRoundNumber,
        'expiration': expiration,
        'duration': duration,
        'rounds': roundsData,
        'started': game.started,
    }

    return gameData

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

def timeOutRound(gameID, roundNumber):
    game = Game.objects.get(id=gameID)
    rnd = PBR.objects.get(game=game, roundNumber=roundNumber)

    if game.currentRound == roundNumber:
        rnd.champion = Champion.objects.get(lolID=0)
        rnd.save()

        nextRoundNumber = roundNumber + 1
        game.currentRound = nextRoundNumber
        game.save()

        try:
            nextRound = PBR.objects.get(game=game, roundNumber=nextRoundNumber)
            startRound(game, nextRound)
        except ObjectDoesNotExist:
            pass

        responseData = getGameData(gameID)
        sendSuccess(Group(str(gameID)), responseData)
