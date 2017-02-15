import json
from channels import Group
from channels.auth import channel_session_user_from_http, channel_session_user
from .utils import validatePick, makePick, sendError,\
                   sendSuccess, getRoundsData


@channel_session_user_from_http
def pick_connect(message, **kwargs):
    message.reply_channel.send({'accept': True})

    gameID = kwargs['pk']
    roundData = getRoundsData(gameID)
    responseData = {'rounds': roundData}

    sendSuccess(message.reply_channel, responseData)
    Group(kwargs['pk']).add(message.reply_channel)

@channel_session_user
def pick_receive(message, **kwargs):
    user = message.user
    messageJSON = json.loads(message.content['text'])
    pickID = messageJSON.get('pick')
    gameID = kwargs['pk']

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
    roundData = getRoundsData(gameID)
    responseData = {'rounds': roundData}

    sendSuccess(Group(gameID), responseData)
    return

@channel_session_user
def pick_disconnect(message, **kwargs):
    Group(kwargs['pk']).discard(message.reply_channel)
