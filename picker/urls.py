from django.conf.urls import url
from django.contrib.auth import views as authViews
from picker.views import IndexView, GameView, NewGameView

urlpatterns = [
    url(r'^$', IndexView.as_view()),
    url(r'^game/(?P<pk>[0-9]+)/$', GameView.as_view(), name="game-view"),
    url(r'^new/game/$', NewGameView.as_view(), name="new-game-view"),
    url(r'^login/$', authViews.login, name="login"),
    url(r'^logout/$', authViews.logout, {'next_page': '/'}, name="logout"),
]
