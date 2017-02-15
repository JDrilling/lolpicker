import requests
import os
from picker.models import Champion
from loadscripts.riotAPI import KEY

BASE_ENDPOINT = "https://global.api.pvp.net"
STATIC_DATA_ENDPOINT = BASE_ENDPOINT + "/api/lol/static-data/NA/v1.2"
CHAMPION_DATA_ENDPOINT = STATIC_DATA_ENDPOINT + "/champion"

PARTIAL_IMAGE_URL = "http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{image}"

LOCAL_STORAGE = os.path.join('..', 'picker', 'static', 'images', 'champions')

def loadAllChampions():
    params = {}
    params['locale'] = "en_US"
    params['dataById'] = "true"
    params['champData'] = "image"
    params['api_key'] = KEY

    response = requests.get(CHAMPION_DATA_ENDPOINT, params=params)
    responseDict = response.json()

    championDataDict = responseDict['data']
    version = responseDict['version']

    for ID, data in championDataDict.items():
        championName = data['name']
        imageName = data['image']['full']
        imageURL = PARTIAL_IMAGE_URL.format(version=version, image=imageName)

        champ, new = Champion.objects.get_or_create(lolID=ID)

        changed = False

        if new:
            changed = True
        if champ.name != championName:
            changed = True
            champ.name=championName
        if champ.imageURL != imageURL:
            changed = True
            champ.imageURL=imageURL

        if changed:
            champ.save()
            print("New champion: {}".format(champ))
