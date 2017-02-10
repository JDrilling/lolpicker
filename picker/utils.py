from picker.models import PickBanRound as PBR

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
