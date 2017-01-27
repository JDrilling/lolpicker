from picker.models import PickBanRound as PBR


TEN_BAN_SCHEME = [PBR.BLUE_BAN,  PBR.RED_BAN,   PBR.BLUE_BAN,
                  PBR.RED_BAN,   PBR.BLUE_BAN,  PBR.RED_BAN, # End Ban 1
                  PBR.BLUE_PICK, PBR.RED_PICK,  PBR.RED_PICK,
                  PBR.BLUE_PICK, PBR.BLUE_PICK, PBR.RED_PICK, # End Pick 1
                  PBR.RED_BAN,   PBR.BLUE_BAN,  PBR.RED_BAN,   PBR.BLUE_BAN, # End Ban 2
                  PBR.RED_PICK,  PBR.BLUE_PICK, PBR.BLUE_PICK, PBR.RED_PICK] # End Pick 2

def createNewTenBanGame(game):
    rounds = []

    for number, typ in enumerate(TEN_BAN_SCHEME):
        pbRound = PBR(game=game, roundNumber=number, roundType=typ)

        rounds.append(pbRound)


    for r in rounds:
        r.save()
