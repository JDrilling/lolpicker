from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views.generic.base import View
from django.db.models import F

from picker.models import Game, Champion, PickBanRound
from picker.forms import GameForm
from picker.utils import createNewTenBanGame


class IndexView(TemplateView):
    template_name = "picker/index.html"


class GameView(SingleObjectMixin, View):
    template_name = "picker/game_detail.html"
    model = Game

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = {'game': self.object}
        context['champions'] = Champion.objects.all().order_by("name")

        return render(request, self.template_name, context)

class NewGameView(FormView):
    template_name = "picker/game_form.html"
    form_class = GameForm
    model = Game

    def form_valid(self, form):
        redTeam = form.cleaned_data['redTeam']
        blueTeam = form.cleaned_data['blueTeam']

        newGame = None
        try:
            newGame = createNewTenBanGame(redTeam, blueTeam)
        except Exception as e:
            print(e)
            return redirect("new-game-view")

        return redirect("game-view", pk=newGame.pk)

