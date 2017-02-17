import requests
import os
import shutil
from urllib.request import urlopen
from picker.models import Champion
from loadscripts.riotAPI import KEY

BASE_ENDPOINT = "https://global.api.pvp.net"
STATIC_DATA_ENDPOINT = BASE_ENDPOINT + "/api/lol/static-data/NA/v1.2"
CHAMPION_DATA_ENDPOINT = STATIC_DATA_ENDPOINT + "/champion"

PARTIAL_IMAGE_URL = "http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{image}"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ALIAS = os.path.join('picker', 'images', 'champions')
LOCAL_STORAGE = os.path.join(BASE_DIR, 'picker', 'static', STATIC_ALIAS)

def getChampFile(champID):
    return os.path.join(LOCAL_STORAGE, "{}.png".format(champID))

def getStaticAlias(champID):
    return os.path.join(STATIC_ALIAS, "{}.png".format(champID))

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
        localPath = getChampFile(ID)
        staticAlias = getStaticAlias(ID)


        champ, new = Champion.objects.get_or_create(lolID=ID)

        changed = False

        if new:
            changed = True
        if champ.name != championName:
            changed = True
            champ.name = championName
        if champ.imageURL != imageURL:
            changed = True
            champ.imageURL = imageURL
        if champ.staticAlias != staticAlias:
            changed = True
            champ.staticAlias = staticAlias

        if changed:
            with urlopen(imageURL) as response, open(localPath, 'wb') as imageFile:
                shutil.copyfileobj(response, imageFile)

            champ.save()
            print("New champion: {}".format(champ))
