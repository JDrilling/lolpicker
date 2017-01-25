from django.conf.urls import url
from picker.views import IndexView, GameView

urlpatterns = [
    url(r'^$', IndexView.as_view()),
    url(r'^game/(?P<pk>[0-9]+)/$', GameView.as_view()),
]
