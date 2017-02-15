from channels.routing import route
from .consumers import pick_receive, pick_connect, pick_disconnect

channel_routing = [
        route("websocket.connect", pick_connect, path=r"^/game/(?P<pk>[0-9]+)/$"),
        route("websocket.disconnect", pick_disconnect, path=r"^/game/(?P<pk>[0-9]+)/$"),
        route("websocket.receive", pick_receive, path=r"^/game/(?P<pk>[0-9]+)/$"),
]
