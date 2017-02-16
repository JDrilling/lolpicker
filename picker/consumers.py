import json
from channels import Group
from channels.auth import channel_session_user_from_http, channel_session_user
from .models import Game
from .utils import validatePick, makePick, sendError,\
                   sendSuccess, getGameData, startPicking


@channel_session_user_from_http
def pick_connect(message, **kwargs):
    message.reply_channel.send({'accept': True})

    gameID = kwargs['pk']
    responseData = getGameData(gameID)

    sendSuccess(message.reply_channel, responseData)
    Group(gameID).add(message.reply_channel)

@channel_session_user
def pick_receive(message, **kwargs):
    user = message.user
    eventJSON = json.loads(message.content['text'])
    eventType = eventJSON['type']
    gameID = kwargs['pk']

    if eventType == 'start':
        game = Game.objects.get(id=gameID)
        if user == game.blueTeam.captain or user == game.redTeam.captain or user.is_staff:
            startPicking(gameID)
            responseData = getGameData(gameID)
            sendSuccess(Group(gameID), responseData)
            return
        else:
            error = "You cannot start this game!"
            sendError(message.reply_channel, error)
            return
    elif eventType == 'pick':

        pickID = eventJSON.get('pick')
        response = {}

        # Validate the pick
        error = validatePick(gameID, pickID, user)

        if error is not None:
            sendError(message.reply_channel, error)
            return

        # Try to make the pick
        error = makePick(gameID, pickID)

        if error is not None:
            sendError(message.reply_channel, error)
            return

        # Send the response
        responseData = getGameData(gameID)

        sendSuccess(Group(gameID), responseData)
        return
    else:
        error = "Unknown event type!"
        sendError(message.reply_channel, error)

@channel_session_user
def pick_disconnect(message, **kwargs):
    Group(kwargs['pk']).discard(message.reply_channel)
